import os
from struct import unpack


# 将通达信的日线文件转换成CSV格式
def day2csv(source_dir, file_name, target_dir):
    # 以二进制方式打开源文件
    source_file = open(source_dir + os.sep + file_name, 'rb')
    buf = source_file.read()
    source_file.close()

    # 打开目标文件，后缀名为CSV
    target_file = open(target_dir + os.sep + file_name + '.csv', 'w')
    buf_size = len(buf)
    rec_count = buf_size / 32
    begin = 0
    end = 32
    header = str('date') + ',' + str('open') + ',' + str('high') + ',' + str('low') + ',' \
             + str('close') + ',' + str('amount') + ',' + str('vol') + '\n'
    target_file.write(header)
    for i in range(int(rec_count)):
        # 将字节流转换成Python数据格式
        # I: unsigned int
        # f: float
        a = unpack('IIIIIfII', buf[begin:end])
        line = str(a[0]) + ',' + str(a[1] / 100.0) + ',' + str(a[2] / 100.0) + ',' \
               + str(a[3] / 100.0) + ',' + str(a[4] / 100.0) + ',' + str(a[5] / 10.0) + ',' \
               + str(a[6]) + '\n'
        target_file.write(line)
        begin += 32
        end += 32
    target_file.close()


source = ['/media/e/tdx/vipdoc/sh/lday', '/media/e/tdx/vipdoc/sz/lday']
target = '/media/e/tdxg'
for s in source:
    file_list = os.listdir(s)
    for f in file_list:
        if f.startswith("sh600") or f.startswith("sz00") or \
                f.startswith("sz30"):
            day2csv(s, f, target)
