"""Baseline submission for diffusion-parabola: a tiny numpy DDPM.

A from-scratch denoising diffusion model with no dependency beyond numpy:

  * a small MLP epsilon-predictor -- input is the noisy point (2D) concatenated
    with a sinusoidal embedding of the diffusion timestep, one hidden stack of
    ReLU units, output is the predicted noise (2D);
  * a linear beta schedule with T diffusion steps;
  * training with a hand-rolled Adam optimizer and manual backprop of the
    epsilon-prediction MSE loss;
  * ancestral (DDPM) sampling to generate new points.

More training `steps` measurably lowers the Chamfer distance, so this baseline
is worth iterating on: run cheaply at steps=1000, graduate to steps=10000.
"""

import numpy as np

# Diffusion / model hyperparameters.
T = 40                    # number of diffusion timesteps
BETA_MIN = 1e-4
BETA_MAX = 0.25
TIME_EMB_DIM = 16         # sinusoidal timestep embedding width
HIDDEN = 64               # hidden width
BATCH = 256
LR = 2e-3
ADAM_B1, ADAM_B2, ADAM_EPS = 0.9, 0.999, 1e-8


def _beta_schedule():
    betas = np.linspace(BETA_MIN, BETA_MAX, T)
    alphas = 1.0 - betas
    alpha_bar = np.cumprod(alphas)
    return betas, alphas, alpha_bar


def _time_embedding(t_norm):
    """Sinusoidal embedding of a batch of normalized timesteps in [0, 1]."""
    t_norm = np.asarray(t_norm, dtype=float).reshape(-1, 1)
    half = TIME_EMB_DIM // 2
    freqs = np.exp(np.linspace(0.0, np.log(1000.0), half))  # (half,)
    args = t_norm * freqs[None, :]                           # (B, half)
    return np.concatenate([np.sin(args), np.cos(args)], axis=1)  # (B, TIME_EMB_DIM)


class _MLP:
    """Two-hidden-layer ReLU MLP with manual forward/backward and Adam."""

    def __init__(self, in_dim, hidden, out_dim, rng):
        def he(shape):
            return rng.standard_normal(shape) * np.sqrt(2.0 / shape[0])

        self.params = {
            "W1": he((in_dim, hidden)), "b1": np.zeros(hidden),
            "W2": he((hidden, hidden)), "b2": np.zeros(hidden),
            "W3": he((hidden, out_dim)) * 0.1, "b3": np.zeros(out_dim),
        }
        # Adam moments.
        self.m = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.v = {k: np.zeros_like(v) for k, v in self.params.items()}
        self.t = 0

    def forward(self, x):
        p = self.params
        z1 = x @ p["W1"] + p["b1"]
        h1 = np.maximum(z1, 0.0)
        z2 = h1 @ p["W2"] + p["b2"]
        h2 = np.maximum(z2, 0.0)
        out = h2 @ p["W3"] + p["b3"]
        self._cache = (x, z1, h1, z2, h2)
        return out

    def backward(self, dout):
        x, z1, h1, z2, h2 = self._cache
        p = self.params
        grads = {}
        grads["W3"] = h2.T @ dout
        grads["b3"] = dout.sum(0)
        dh2 = dout @ p["W3"].T
        dz2 = dh2 * (z2 > 0)
        grads["W2"] = h1.T @ dz2
        grads["b2"] = dz2.sum(0)
        dh1 = dz2 @ p["W2"].T
        dz1 = dh1 * (z1 > 0)
        grads["W1"] = x.T @ dz1
        grads["b1"] = dz1.sum(0)
        return grads

    def adam_step(self, grads, lr):
        self.t += 1
        for k in self.params:
            g = grads[k]
            self.m[k] = ADAM_B1 * self.m[k] + (1 - ADAM_B1) * g
            self.v[k] = ADAM_B2 * self.v[k] + (1 - ADAM_B2) * (g * g)
            m_hat = self.m[k] / (1 - ADAM_B1 ** self.t)
            v_hat = self.v[k] / (1 - ADAM_B2 ** self.t)
            self.params[k] -= lr * m_hat / (np.sqrt(v_hat) + ADAM_EPS)


def train_and_sample(data, *, steps, n_samples, seed):
    """Train a numpy DDPM on `data` and return `n_samples` generated points."""
    rng = np.random.default_rng(seed)
    data = np.asarray(data, dtype=float)

    # Normalize to zero mean / unit std; samples are un-normalized at the end.
    mean = data.mean(0)
    std = data.std(0) + 1e-8
    x0_all = (data - mean) / std
    n = len(x0_all)

    betas, alphas, alpha_bar = _beta_schedule()
    sqrt_ab = np.sqrt(alpha_bar)
    sqrt_1m_ab = np.sqrt(1.0 - alpha_bar)

    model = _MLP(2 + TIME_EMB_DIM, HIDDEN, 2, rng)

    for _ in range(int(steps)):
        idx = rng.integers(0, n, BATCH)
        x0 = x0_all[idx]
        t = rng.integers(0, T, BATCH)
        eps = rng.standard_normal((BATCH, 2))

        x_t = sqrt_ab[t][:, None] * x0 + sqrt_1m_ab[t][:, None] * eps
        temb = _time_embedding(t / T)
        inp = np.concatenate([x_t, temb], axis=1)

        eps_pred = model.forward(inp)
        # MSE over batch and dims; d/dpred = 2*(pred-eps)/(B*2).
        dout = (eps_pred - eps) / BATCH
        model.adam_step(model.backward(dout), LR)

    # Ancestral sampling from pure noise.
    x = rng.standard_normal((n_samples, 2))
    for step in range(T - 1, -1, -1):
        temb = _time_embedding(np.full(n_samples, step / T))
        eps_pred = model.forward(np.concatenate([x, temb], axis=1))
        mean_coef = 1.0 / np.sqrt(alphas[step])
        x = mean_coef * (x - betas[step] / sqrt_1m_ab[step] * eps_pred)
        if step > 0:
            x = x + np.sqrt(betas[step]) * rng.standard_normal((n_samples, 2))

    return x * std + mean
