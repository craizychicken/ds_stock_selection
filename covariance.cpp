#include <iostream>
#include <vector>
#include <stdexcept>

typedef std::vector<std::vector<double>> matrix;

// Internal implementation — keeps your original logic untouched
matrix calculateCovMatrixInternal(const matrix &data){
    const int m = data.size();
    const int n = data[0].size();

    if (n < 2)
        throw std::invalid_argument("Need at least 2 observations");

    std::vector<double> mean(m, 0.0);
    for (int i = 0; i < m; i++)
        for (int j = 0; j < n; j++)
            mean[i] += data[i][j];
    for (int i = 0; i < m; i++)
        mean[i] /= n;

    matrix cov(m, std::vector<double>(m, 0.0));
    for (int i = 0; i < m; i++)
        for (int j = i; j < m; j++)
            for (int k = 0; k < n; k++)
                cov[i][j] += (data[i][k] - mean[i]) * (data[j][k] - mean[j]);

    for (int i = 0; i < m; i++)
        for (int j = i; j < m; j++){
            cov[i][j] /= (n - 1);
            cov[j][i] = cov[i][j];
        }

    return cov;
}

// Exported function — flat pointers only, C-compatible
extern "C" {
    __declspec(dllexport) void calculateCovMatrix(
        double* data_flat,  // input:  m x n, row-major
        int m,
        int n,
        double* out_flat)   // output: m x m, caller allocates
    {
        // reconstruct matrix
        matrix data(m, std::vector<double>(n));
        for (int i = 0; i < m; i++)
            for (int j = 0; j < n; j++)
                data[i][j] = data_flat[i*n + j];

        // run internal logic
        matrix cov = calculateCovMatrixInternal(data);

        // write to output buffer
        for (int i = 0; i < m; i++)
            for (int j = 0; j < m; j++)
                out_flat[i*m + j] = cov[i][j];
    }
}