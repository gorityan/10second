import tkinter as tk
import threading
import time
import random

class TenSecondTrapGame:
    def __init__(self, root):
        self.root = root
        self.root.title("10秒トラップゲーム")
        self.root.geometry("600x400")
        self.root.configure(bg="#222")
        
        # 変数の初期化
        self.game_over = False
        self.start_time = 0
        self.trap_thread = None
        
        # ゲームの状態
        self.game_state = "standby"  # standby, playing, result
        
        # UI要素の設定
        self.setup_ui()
    
    def setup_ui(self):
        """UIの初期設定"""
        # メインフレーム
        self.main_frame = tk.Frame(self.root, bg="#222")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトルラベル
        self.title_label = tk.Label(
            self.main_frame, 
            text="10秒トラップゲーム", 
            font=("Helvetica", 24, "bold"),
            fg="#FFF",
            bg="#222"
        )
        self.title_label.pack(pady=(0, 20))
        
        # 説明ラベル
        self.instruction_label = tk.Label(
            self.main_frame,
            text="「スタート」ボタンを押すとタイマーが始まります。\n"
                 "ちょうど10秒経ったと思ったら「ストップ」ボタンを押してください！\n"
                 "途中で表示されるメッセージはあなたを惑わせるためのトラップです！",
            font=("Helvetica", 12),
            justify=tk.CENTER,
            fg="#CCC",
            bg="#222",
            wraplength=550
        )
        self.instruction_label.pack(pady=(0, 20))
        
        # メッセージ表示エリア
        self.message_frame = tk.Frame(self.main_frame, bg="#333", bd=2, relief=tk.SUNKEN)
        self.message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        self.message_label = tk.Label(
            self.message_frame,
            text="ゲームを開始するには「スタート」ボタンを押してください",
            font=("Helvetica", 14),
            fg="#FFF",
            bg="#333",
            wraplength=550,
            height=8
        )
        self.message_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ボタンフレーム
        self.button_frame = tk.Frame(self.main_frame, bg="#222")
        self.button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # スタートボタン
        self.start_button = tk.Button(
            self.button_frame,
            text="スタート",
            font=("Helvetica", 14, "bold"),
            bg="#007BFF",
            fg="#FFF",
            activebackground="#0056b3",
            activeforeground="#FFF",
            padx=20,
            pady=10,
            command=self.start_game
        )
        self.start_button.pack(side=tk.LEFT, padx=(120, 10))
        
        # ストップボタン（初期状態では無効）
        self.stop_button = tk.Button(
            self.button_frame,
            text="ストップ",
            font=("Helvetica", 14, "bold"),
            bg="#DC3545",
            fg="#FFF",
            activebackground="#c82333",
            activeforeground="#FFF",
            padx=20,
            pady=10,
            state=tk.DISABLED,
            command=self.stop_game
        )
        self.stop_button.pack(side=tk.RIGHT, padx=(10, 120))
        
        # 結果表示ラベル
        self.result_label = tk.Label(
            self.main_frame,
            text="",
            font=("Helvetica", 12, "bold"),
            fg="#FFC107",
            bg="#222"
        )
        self.result_label.pack(pady=(0, 10))
    
    def start_game(self):
        """ゲームを開始する"""
        self.game_state = "playing"
        self.game_over = False
        
        # UIの状態を更新
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.message_label.config(text="タイマースタート！\n10秒だと思ったら「ストップ」ボタンを押してください")
        self.result_label.config(text="")
        
        # 開始時間を記録
        self.start_time = time.time()
        
        # トラップメッセージを表示するスレッドを開始
        self.trap_thread = threading.Thread(target=self.display_trap_messages)
        self.trap_thread.daemon = True
        self.trap_thread.start()
    
    def stop_game(self):
        """ゲームを停止し、結果を表示する"""
        if self.game_state != "playing":
            return
            
        self.game_state = "result"
        self.game_over = True
        
        # 終了時間を記録
        end_time = time.time()
        
        # 経過時間を計算
        elapsed_time = end_time - self.start_time
        
        # UIの状態を更新
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.message_label.config(text=f"ゲーム終了！\nあなたの記録: {elapsed_time:.3f}秒\n10秒との差: {abs(elapsed_time - 10):.3f}秒")
        
        # 評価を表示
        if abs(elapsed_time - 10) < 0.1:
            evaluation = "評価: 素晴らしい！ほぼ完璧な10秒感覚です！"
        elif abs(elapsed_time - 10) < 0.5:
            evaluation = "評価: すごい！かなり正確な時間感覚をお持ちです"
        elif abs(elapsed_time - 10) < 1.0:
            evaluation = "評価: なかなか良いですね！"
        elif abs(elapsed_time - 10) < 2.0:
            evaluation = "評価: もう少し練習しましょう"
        else:
            evaluation = "評価: トラップにはまってしまいましたね..."
        
        self.result_label.config(text=evaluation)
    
    def display_trap_messages(self):
        """トラップメッセージを表示するスレッド関数"""
        # ゲームが終了するまでループ
        while not self.game_over:
            # ランダムな待機時間（1〜3秒）
            wait_time = random.uniform(1.0, 3.0)
            time.sleep(wait_time)
            
            # ゲームが終了していなければメッセージを表示
            if not self.game_over and self.game_state == "playing":
                trap_message = self.generate_trap_message()
                # UIスレッドでメッセージを更新するため、afterメソッドを使用
                self.root.after(0, lambda msg=trap_message: self.update_message(msg))
    
    def update_message(self, message):
        """UIスレッドでメッセージを更新する"""
        self.message_label.config(text=message)
    
    def generate_trap_message(self):
        """ランダムなトラップメッセージを生成する"""
        messages = [
            "3秒経過！",  # フェイクの経過時間
            "5秒経過！",
            "7秒経過！",
            "9秒経過！",
            "11秒経過！",
            "もう10秒経ったかも？",
            "まだ5秒も経ってないよ",
            "そろそろ押したほうがいいかも...",
            "もう少し待った方がいいな",
            "時計の針は意外と早く進むものだよ",
            "人間の時間感覚は意外と不正確",
            "焦らないで、落ち着いて...",
            "ちなみに、人間が1秒を数えるときの平均誤差は約200ミリ秒です",
            "ヒント：今が押し時！",
            "早く押して！時間がない！",
            "まだまだ全然早いよ",
            "数学的に考えれば、10秒は10^1秒です",
            "ゆっくり呼吸して数えてみては？",
            "時間は感覚ではなく、物理的な実体です",
            "急がば回れ、慌てると失敗するよ",
        ]
        return random.choice(messages)

# アプリケーションを実行
if __name__ == "__main__":
    root = tk.Tk()
    app = TenSecondTrapGame(root)
    root.mainloop()