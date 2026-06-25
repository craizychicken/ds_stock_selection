#include <iostream>
#include <vector>
#include <stdexcept>

typedef std::vector<std::vector<double>> matrix;

// Internal implementation — keeps your original logic untouched
matrix calculateCovMatrixInternal(const matrix &data){
    const int rows = data.size();
    const int cols = data[0].size();

    if (rows < 2){
        throw std::invalid_argument("Need at least 2 observations");
    }

    std::vector<double> mean(cols, 0.0);
    // Get sum
    for (int i = 0; i < rows; i++){
        for (int j = 0; j < cols; j++){
            mean[j] += data[i][j];
        }
    }
    // normalise sum to get mean
    for (int i = 0; i < cols; i++){
        mean[i] /= rows;
    }

    matrix cov(cols, std::vector<double>(cols, 0.0));
    // Get sum of (x-E[X])(y-E[Y])
    for (int i = 0; i < cols; i++){
        for (int j = i; j < cols; j++){
            for (int k = 0; k < rows; k++){
                cov[i][j] += (data[k][i] - mean[i]) * (data[k][j] - mean[j]);
            }
            // Normalise
            cov[i][j] /= (rows - 1);
            cov[j][i] = cov[i][j];
        }
    }

    return cov;
}

// Exported function — flat pointers only, C-compatible
extern "C" {
    void calculateCovMatrix(
        double* data_flat,  // input:  n x m, row-major
        int rows,
        int cols,
        double* out_flat)   // output: m x m, caller allocates
    {
        // reconstruct matrix
        matrix data(rows, std::vector<double>(cols));
        for (int i = 0; i < rows; i++){
            for (int j = 0; j < cols; j++){
                data[i][j] = data_flat[i*cols + j];
            }
        }

        // run internal logic
        matrix cov = calculateCovMatrixInternal(data);

        // write to output buffer
        for (int i = 0; i < cols; i++){
            for (int j = 0; j < cols; j++){
                out_flat[i*cols + j] = cov[i][j];
            }
        }
    }
}