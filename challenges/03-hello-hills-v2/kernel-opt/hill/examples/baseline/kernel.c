/* Naive row-major SGEMM: the starting point every optimization is measured against. */
void gemm(int n, const float *A, const float *B, float *C) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++) {
            float acc = 0.0f;
            for (int k = 0; k < n; k++)
                acc += A[i * n + k] * B[k * n + j];
            C[i * n + j] = acc;
        }
}
