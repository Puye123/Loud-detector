import myaudio
import time
import os
from datetime import datetime
from glob import glob
import numpy as np
import matplotlib.pyplot as plt

import socket

# init socket server
ip_address = '192.168.1.20'
port = 18888
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((ip_address, port))
s.listen(5)

print('waiting for connetcion...')
clientsocket, address = s.accept()
print('connect: ' + str(address))

myaudio = myaudio.MyAudio(chunk=1024)
myaudio.run()
VOLUME_THRESHOLD = 200000 # 検出したい音量閾値
FREQUENCY_MIN = 100
FREQUENCY_MAX = 1000

LOUD_COUNT_THRESHOLD = 3 # この回数分連続で大きな音を検知したら音声保存&通知

AUDIO_LOG_DIR = 'audio_log/' # 音声ログデータの保存フォルダ
AUDIO_LOG_MAX_NUM = 10 # 保存する音声データ数の最大数

DEBUG_MODE = True # グラフ表示をオフにしたい場合はFalse

is_first = True
loud_count = 0
while True:
    try:
        data = myaudio.get_one_sample()
        if is_first == True:
            time.sleep(1)
            is_first = False
            continue
        # 周波数解析を行い、人の声か否かを推定
        fft = np.fft.fft(data)
        fft = np.abs(fft)
        x = np.linspace(0, myaudio.rate, myaudio.chunk)
        x = x[0:int(myaudio.chunk/2)]
        y = fft[0:int(myaudio.chunk/2)]
        peak_hz = x[np.argmax(y)]
        max_power = np.max(y)
        if DEBUG_MODE:
            title = str(int(peak_hz)) + 'Hz : ' + str(int(max_power))
            plt.title(title)
            plt.ylim(0, int(VOLUME_THRESHOLD * 1.5))
            plt.plot(x, y)
            plt.hlines([VOLUME_THRESHOLD], FREQUENCY_MIN, FREQUENCY_MAX, colors='red', linestyles='solid')
            plt.vlines([FREQUENCY_MIN, FREQUENCY_MAX], 0, int(VOLUME_THRESHOLD * 1.5), colors='blue', linestyles='dashed')
            plt.draw()
            plt.pause(0.001)
            plt.cla()
        if max_power > VOLUME_THRESHOLD and peak_hz > FREQUENCY_MIN and peak_hz < FREQUENCY_MAX:
            if loud_count < LOUD_COUNT_THRESHOLD:
                loud_count += 1
                continue

            print("Detect loud voice!")
            # ソケット通信
            clientsocket.send(bytes("Detect big voice!", 'utf-8'))

            # 音声ログファイル保存
            filename = AUDIO_LOG_DIR + datetime.today().strftime("%Y%m%d%H%M%S") + ".wav"
            print('save: ', filename)
            existing_log_files = glob(AUDIO_LOG_DIR + "*.wav")
            
            if len(existing_log_files) >= AUDIO_LOG_MAX_NUM:
                # 既に最大数の音声ログファイルが存在していたら、古い音声ログファイルを消去する。
                existing_log_files.sort()
                os.remove(existing_log_files[0])

            myaudio.save_file(filename, second=5)
            time.sleep(2)
            loud_count = 0
        else:
            loud_count = 0

    except KeyboardInterrupt:
        print('Keyboard Interrupt!!')
        break

    except Exception as ex:
        print('Unexpected exception!!')
        print(ex)
        break

del(myaudio)
clientsocket.close()
s.close()