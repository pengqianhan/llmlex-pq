import base64

# 1. 读取原始图片
with open("ha_image.png", "rb") as f:
    original_data = f.read()

# 2. 编码成 base64 文本
encoded = base64.b64encode(original_data)

# 3. 再解码回二进制
decoded = base64.b64decode(encoded)

# 4. 比较原始数据与解码结果是否完全一致
print("是否完全一致：", original_data == decoded)
