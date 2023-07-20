import cv2
import numpy as np

def detect_yellow_squares(image_path):
    # 读取图像
    image = cv2.imread(image_path)

    # 将图像从BGR色彩空间转换为HSV色彩空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 设定黄色的HSV范围
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([40, 255, 255])

    # 根据HSV范围对图像进行二值化，提取黄色部分
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 筛选方形焊点
    yellow_squares = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
        if len(approx) == 4:
            yellow_squares.append(approx)

    # 绘制边界框
    for square in yellow_squares:
        cv2.drawContours(image, [square], 0, (255, 0, 0), 2)  # 绘制黄色边界框

    # 显示图像
    cv2.imshow('Detected Yellow Squares', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 使用示例
image_path = 'data/20230719154919.png'
detect_yellow_squares(image_path)
