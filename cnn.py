import numpy as np

def relu(input_data):
    if input_data.ndim == 2:
        input_data = input_data[np.newaxis,:,:]
    
    C, H, W = input_data.shape
    output_data = np.copy(input_data)

    for c in range(C):
        for i in range(H):
            for j in range(W):
                if output_data[c,i,j] < 0:
                    output_data[c,i,j] = 0
    return output_data.squeeze()

def max_pooling(input_data, pool_size=2, stride=2):
    if input_data.ndim == 2:  # 單通道
        input_data = input_data[np.newaxis, :, :]  # 變成 (1, H, W) np.newaxis是新增一個維度
        
    C, H, W = input_data.shape 
    out_H = (H - pool_size) // stride + 1
    out_W = (W - pool_size) // stride + 1
    output = np.zeros((C, out_H, out_W))

    for c in range(C):
        for i in range(out_H):
            for j in range(out_W):
                h_start = i * stride
                h_end = h_start + pool_size
                w_start = j * stride
                w_end = w_start + pool_size

                region = input_data[c, h_start:h_end, w_start:w_end]
                output[c, i, j] = np.max(region)
    
    return output.squeeze()  # 若只有單通道，拿掉大小為 1 的維度

def flatten(input_data):
    if input_data.ndim == 2:
        input_data = input_data[np.newaxis,:,:]
    C, H, W = input_data.shape
    output_data = np.zeros(C * H * W)  # 建立一個 1D 的 numpy 陣列
    index = 0
    for c in range(C):
        for i in range(H):
            for j in range(W):
                output_data[index] = input_data[c][i][j]
                index += 1
    return output_data

def softmax(input_data):
    # 若是 1 維向量，轉成 2 維形式統一處理
    if input_data.ndim == 1:
        input_data = input_data[np.newaxis, :]  # shape: (1, N)
    
    # 數值穩定技巧：減去每一 row 的最大值
    input_stable = input_data - np.max(input_data, axis=1, keepdims=True)
    exp_data = np.exp(input_stable)
    sum_exp = np.sum(exp_data, axis=1, keepdims=True)
    output = exp_data / sum_exp  # broadcasting 除法

    return output.squeeze()  # 如果原本是一維，壓回去

def dense(input_data, weight, bias):
    """
    input_data: 1D numpy array, shape = (input_dim,)
    weight: 2D numpy array, shape = (output_dim, input_dim)
    bias: 1D numpy array, shape = (output_dim,)
    return: 1D numpy array, shape = (output_dim,)
    """
    if input_data.ndim != 1:
        raise ValueError("input_data 必須是一維向量")

    return np.dot(weight, input_data) + bias

def conv2d(input_data, kernel, stride=1):
    """
    input_data: numpy array, shape = (H, W)
    kernel: numpy array, shape = (kH, kW)
    stride: int
    
    return: numpy array, shape = (out_H, out_W)
    """
    H, W = input_data.shape
    kH, kW = kernel.shape

    out_H = (H - kH) // stride + 1
    out_W = (W - kW) // stride + 1

    output = np.zeros((out_H, out_W))

    for i in range(out_H):
        for j in range(out_W):
            h_start = i * stride
            w_start = j * stride
            region = input_data[h_start:h_start + kH, w_start:w_start + kW]
            output[i, j] = np.sum(region * kernel)

    return output