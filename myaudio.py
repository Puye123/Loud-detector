import pyaudio
import wave
import numpy as np

class MyAudio():
    def __init__(self, chunk=1024, channels=1, rate=44100):
        """ コンストラクタ
            インスタンス生成

        Args:
            chunk (int, optional): マイクから音を取り出す際の１回当たりのデータサイズ. Defaults to 1024.
            channels (int, optional): チャネル数. Defaults to 1.
            rate (int, optional): サンプリング周波数. Defaults to 44100.
        """
        self.chunk = chunk
        self.channels = channels
        self.rate = rate
        self.format = pyaudio.paInt16
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None

    def __del__(self):
        """ デストラクタ
            音声ストリームを閉じてインスタンスを破棄する
        """
        if self.stream is not None:
            self.stream.close()
        self.pyaudio.terminate()

    def run(self):
        """音声ストリーム開始
        """
        self.stream = self.pyaudio.open(
            rate=self.rate, channels=self.channels,
            format=self.format, input=True, 
            frames_per_buffer=self.chunk
        )

    def get_one_sample(self):
        """1サンプル分のデータを取得する

        Returns:
            ndarray: 音声データ
        """
        buffer = self.stream.read(self.chunk, exception_on_overflow=False)
        data = np.frombuffer(buffer, dtype=np.int16).astype(np.float32)
        return data

    def get_many_samples(self, second):
        """指定した秒数分の音声データを取得

        Args:
            second (int, optional): 秒数.

        Returns:
            ndarray: 音声データ
        """
        buffer = self.stream.read(self.chunk, exception_on_overflow=False)
        audio_data = []
        audio_data.append(buffer)
        for i in range(0, int(self.rate / self.chunk * int(second))):
            buffer = self.stream.read(self.chunk,  exception_on_overflow=False)
            audio_data.append(buffer)
        audio_data = b''.join(audio_data) # バイト文字列結合
        return audio_data

    def save_file(self, filename, second=3):
        """指定した秒数分の音声データをキャプチャしてファイルに保存

        Args:
            filename (str): ファイル名
            second (int, optional): キャプチャしたい秒数. Defaults to 3.
        """
        data = self.get_many_samples(second)
        wave_out = wave.open(filename, 'w')
        wave_out.setnchannels(self.channels)
        wave_out.setsampwidth(2) # 16bit = 2Byte
        wave_out.setframerate(self.rate)
        wave_out.writeframes(data)
        wave_out.close()

