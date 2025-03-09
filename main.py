# 10秒トラップゲーム
# 秒数を測定する感覚を鍛えるゲームで、様々なトラップで惑わされながら10秒を数えるゲーム

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
        self.timer_visible = False
        self.timer_value = 0
        self.timer_after_id = None
        self.fake_timer_after_id = None
        self.show_fake_timer = False
        
        # トラップ管理用の変数
        self.active_traps = {
            "message": False,  # テキストメッセージトラップ
            "visual": False,   # 視覚的トラップ（色変更など）
            "timer": False,    # タイマー関連トラップ
            "system": False    # システムメッセージトラップ
        }
        
        # ゲームの状態
        self.game_state = "standby"  # standby, playing, result
        
        # エンターキーのバインド
        self.root.bind('<Return>', self.handle_enter_key)
        
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
            text="「スタート」ボタンを押すか、Enterキーを押すとタイマーが始まります。\n"
                 "ちょうど10秒経ったと思ったら「ストップ」ボタンを押すか、再度Enterキーを押してください！\n"
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
        self.message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.message_label = tk.Label(
            self.message_frame,
            text="ゲームを開始するには「スタート」ボタンまたはEnterキーを押してください",
            font=("Helvetica", 14),
            fg="#FFF",
            bg="#333",
            wraplength=550,
            height=8
        )
        self.message_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイマー表示用の専用フレーム（常に存在する）
        self.timer_frame = tk.Frame(self.main_frame, bg="#222", height=50)
        self.timer_frame.pack(fill=tk.X, pady=(0, 10))
        self.timer_frame.pack_propagate(False)  # フレームサイズを固定
        
        # タイマー表示ラベル
        self.timer_label = tk.Label(
            self.timer_frame,
            text="",
            font=("Helvetica", 36, "bold"),
            fg="#00FFFF",
            bg="#222"
        )
        self.timer_label.pack(expand=True)
        # タイマーラベルは表示されていても、timer_frameは常に存在する
        
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
        self.start_button.pack(side=tk.LEFT, padx=(60, 10))
        
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
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # 終了ボタン
        self.exit_button = tk.Button(
            self.button_frame,
            text="終了",
            font=("Helvetica", 14, "bold"),
            bg="#6C757D",
            fg="#FFF",
            activebackground="#5a6268",
            activeforeground="#FFF",
            padx=20,
            pady=10,
            command=self.exit_game
        )
        self.exit_button.pack(side=tk.LEFT, padx=(10, 60))
        
        # 結果表示ラベル
        self.result_label = tk.Label(
            self.main_frame,
            text="",
            font=("Helvetica", 12, "bold"),
            fg="#FFC107",
            bg="#222"
        )
        self.result_label.pack(pady=(0, 10))
    
    def handle_enter_key(self, event):
        """Enterキーが押されたときの処理"""
        if self.game_state == "standby" or self.game_state == "result":
            self.start_game()
        elif self.game_state == "playing":
            self.stop_game()
    
    def exit_game(self):
        """ゲームを終了し、ウィンドウを閉じる"""
        if hasattr(self, 'trap_thread') and self.trap_thread and self.trap_thread.is_alive():
            self.game_over = True
        
        # タイマー更新があれば停止
        if hasattr(self, 'timer_after_id') and self.timer_after_id:
            self.root.after_cancel(self.timer_after_id)
            
        # 偽タイマー更新があれば停止
        if hasattr(self, 'fake_timer_after_id') and self.fake_timer_after_id:
            self.root.after_cancel(self.fake_timer_after_id)
            
        self.root.destroy()
    
    def show_timer(self, value):
        """タイマーを表示する"""
        self.timer_value = value
        self.timer_label.config(text=f"{value:.1f}")
        self.timer_visible = True
    
    def hide_timer(self):
        """タイマーを非表示にする"""
        if self.timer_visible and self.game_state == "playing":
            self.timer_visible = False
            self.timer_label.config(text="")
    
    def start_fake_timer(self):
        """偽のタイマーを開始する（惑わすため）"""
        if self.game_state == "playing" and not self.timer_visible and not self.game_over:
            self.show_fake_timer = True
            self.timer_visible = True
            self.timer_label.config(fg="#FF9500")  # 色を変更して偽タイマーであることをわかりにくくする
            self.update_fake_timer()
            
            # 3秒後に偽タイマーを非表示にする
            self.root.after(3000, self.hide_fake_timer)
    
    def hide_fake_timer(self):
        """偽のタイマーを非表示にする"""
        if self.timer_visible and self.show_fake_timer and self.game_state == "playing":
            self.timer_visible = False
            self.show_fake_timer = False
            self.timer_label.config(text="")
    
    def update_fake_timer(self):
        """偽のタイマー値を更新する（実際の時間とは無関係）"""
        if self.game_state == "playing" and self.show_fake_timer and self.timer_visible:
            # 実際の時間とは異なる偽の値を表示（惑わす効果）
            elapsed = time.time() - self.start_time
            
            # 偽のタイマー値を生成（実際より速かったり遅かったりする）
            if elapsed < 7:
                # 実際より早く進む偽タイマー
                fake_value = elapsed * random.uniform(1.2, 1.4)
            else:
                # 実際より遅く進む偽タイマー
                fake_value = elapsed * random.uniform(0.7, 0.9)
                
            # たまに不自然な値にジャンプ
            if random.random() < 0.05:  # 5%の確率
                if fake_value < 5:
                    fake_value += random.uniform(1, 2)
                else:
                    fake_value -= random.uniform(1, 2)
            
            self.timer_label.config(text=f"{fake_value:.1f}")
            
            # 次の更新をスケジュール（0.1秒ごと）
            if self.show_fake_timer:
                self.fake_timer_after_id = self.root.after(100, self.update_fake_timer)
    
    def update_timer(self):
        """実際のタイマー値を更新する（最初の3秒間のみ）"""
        if self.game_state == "playing":
            # 経過時間を計算
            elapsed_time = time.time() - self.start_time
            
            # タイマーが表示中で、偽タイマーでなければ値を更新
            if self.timer_visible and not self.show_fake_timer:
                self.timer_label.config(text=f"{elapsed_time:.1f}")
            
            # 次の更新をスケジュール（0.1秒ごと）
            self.timer_after_id = self.root.after(100, self.update_timer)
    
    def start_game(self):
        """ゲームを開始する"""
        self.game_state = "playing"
        self.game_over = False
        
        # UIの状態を更新
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.message_label.config(text="タイマースタート！\n10秒だと思ったら「ストップ」ボタンを押してください")
        self.result_label.config(text="")
        
        # トラップ状態をリセット
        for key in self.active_traps:
            self.active_traps[key] = False
        
        # 開始時間を記録
        self.start_time = time.time()
        
        # 初期タイマーを表示（これは正確なタイマー）
        self.show_timer(0)
        
        # 3秒後にタイマーを非表示にするスケジュール
        self.root.after(3000, self.hide_timer)
        
        # 5秒後に偽のタイマーを表示するスケジュール
        self.root.after(5000, self.start_fake_timer)
        
        # トラップメッセージを表示するスレッドを開始
        self.trap_thread = threading.Thread(target=self.display_trap_messages)
        self.trap_thread.daemon = True
        self.trap_thread.start()
        
        # タイマー更新を開始
        self.update_timer()
    
    def stop_game(self):
        """ゲームを停止し、結果を表示する"""
        if self.game_state != "playing":
            return
            
        self.game_state = "result"
        self.game_over = True
        
        # タイマーが表示されていたら非表示にする
        if self.timer_visible:
            self.timer_visible = False
            self.timer_label.config(text="")
            self.show_fake_timer = False
        
        # 終了時間を記録
        end_time = time.time()
        
        # 経過時間を計算
        elapsed_time = end_time - self.start_time
        
        # UIの状態を更新
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # 背景色を元に戻す
        self.message_frame.config(bg="#333")
        
        # トラップ状態をリセット（全ての進行中のトラップをキャンセル）
        for key in self.active_traps:
            self.active_traps[key] = False
        
        # たまに（10%の確率で）偽の結果を表示するトラップを仕掛ける（すぐに本当の結果に切り替わる）
        if random.random() < 0.1 and elapsed_time > 5:
            fake_time = random.uniform(max(1, elapsed_time - 5), elapsed_time + 5)
            fake_diff = abs(fake_time - 10)
            
            self.message_label.config(
                text=f"ゲーム終了！\nあなたの記録: {fake_time:.3f}秒\n10秒との差: {fake_diff:.3f}秒",
                fg="#FF9500"
            )
            
            if fake_diff < 0.1:
                fake_eval = "評価: 素晴らしい！ほぼ完璧な10秒感覚です！"
            elif fake_diff < 0.5:
                fake_eval = "評価: すごい！かなり正確な時間感覚をお持ちです"
            elif fake_diff < 1.0:
                fake_eval = "評価: なかなか良いですね！"
            elif fake_diff < 2.0:
                fake_eval = "評価: もう少し練習しましょう"
            else:
                fake_eval = "評価: トラップにはまってしまいましたね..."
            
            self.result_label.config(text=fake_eval, fg="#FF9500")
            
            # 1.5秒後に本当の結果を表示
            self.root.after(1500, lambda: self.display_real_result(elapsed_time))
        else:
            # 通常の結果表示
            self.display_real_result(elapsed_time)
    
    def display_real_result(self, elapsed_time):
        """実際の結果を表示する"""
        self.message_label.config(
            text=f"ゲーム終了！\nあなたの記録: {elapsed_time:.3f}秒\n10秒との差: {abs(elapsed_time - 10):.3f}秒",
            fg="#FFF"
        )
        
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
        
        self.result_label.config(text=evaluation, fg="#FFC107")
    
    def generate_trap_message(self):
        """ランダムなトラップメッセージを生成する"""
        # 利用可能なトラップカテゴリを確認
        available_categories = []
        
        # メッセージトラップが利用可能か（表示中でなければ利用可能）
        if not self.active_traps["message"]:
            available_categories.append("text")
            available_categories.append("fake_end")
        
        # 視覚的トラップが利用可能か
        if not self.active_traps["visual"]:
            available_categories.append("color_flash")
        
        # タイマートラップが利用可能か（表示中でなければ利用可能）
        if not self.active_traps["timer"] and not self.timer_visible:
            available_categories.append("timer_jump")
        
        # システムメッセージトラップが利用可能か
        if not self.active_traps["system"]:
            available_categories.append("system_error")
        
        # 利用可能なトラップがない場合は待機
        if not available_categories:
            return {"type": "none"}
        
        # トラップタイプの確率設定（利用可能なもののみ）
        weights = []
        for category in available_categories:
            if category == "text":
                weights.append(50)
            elif category == "fake_end":
                weights.append(25)
            elif category == "color_flash":
                weights.append(10)
            elif category == "timer_jump":
                weights.append(10)
            elif category == "system_error":
                weights.append(5)
        
        # 重みの合計が100になるように正規化
        total_weight = sum(weights)
        normalized_weights = [w * 100 / total_weight for w in weights]
        
        # トラップの種類を決定
        trap_type = random.choices(
            available_categories,
            weights=normalized_weights,
            k=1
        )[0]
        
        if trap_type == "text":
            # 通常のテキストトラップ
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
            return {"type": "text", "message": random.choice(messages)}
        
        elif trap_type == "fake_end":
            # ダミーの記録表示トラップ
            fake_time = random.uniform(8.5, 11.5)
            messages = [
                f"ゲーム終了！\nあなたの記録: {fake_time:.3f}秒\n10秒との差: {abs(fake_time - 10):.3f}秒",
                f"タイムアップ！\n記録: {fake_time:.3f}秒",
                f"計測終了\n{fake_time:.3f}秒でした"
            ]
            return {"type": "fake_end", "message": random.choice(messages)}
        
        elif trap_type == "color_flash":
            # 画面フラッシュトラップ
            colors = ["#FF5555", "#55FF55", "#5555FF", "#FFFF55", "#FF55FF"]
            return {"type": "color_flash", "color": random.choice(colors)}
        
        elif trap_type == "timer_jump":
            # 偽タイマーを一瞬表示するトラップ
            fake_time = random.uniform(7.0, 12.0)
            return {"type": "timer_jump", "time": fake_time}
        
        elif trap_type == "system_error":
            # システムエラー風トラップ
            errors = [
                "エラー: タイマーが同期できません。再起動してください。",
                "警告: メモリ不足により計測精度が低下しています",
                "システム通知: バッテリー残量低下のため、タイマーが停止する可能性があります",
                "エラー: バックグラウンドプロセスがタイマーに干渉しています",
                "セキュリティ警告: 不正なアクセスが検出されました"
            ]
            return {"type": "system_error", "message": random.choice(errors)}
        
        return {"type": "none"}  # デフォルト
    
    def display_trap_messages(self):
        """トラップメッセージを表示するスレッド関数"""
        # ゲームが終了するまでループ
        while not self.game_over:
            # ランダムな待機時間（1〜3秒）
            wait_time = random.uniform(1.0, 3.0)
            time.sleep(wait_time)
            
            # ゲームが終了していなければトラップを表示
            if not self.game_over and self.game_state == "playing":
                trap = self.generate_trap_message()
                # UIスレッドでトラップを実行するため、afterメソッドを使用
                if trap["type"] != "none":
                    self.root.after(0, lambda t=trap: self.execute_trap(t))
    
    def execute_trap(self, trap):
        """トラップの種類に応じた処理を実行する"""
        # ゲームが終了している場合は何もしない
        if self.game_state != "playing":
            return
            
        if trap["type"] == "none":
            # 利用可能なトラップがない場合は何もしない
            return
            
        elif trap["type"] == "text":
            # 通常のテキストメッセージ
            if not self.active_traps["message"]:
                self.active_traps["message"] = True
                self.message_label.config(text=trap["message"])
                
                # 2秒後にメッセージトラップを解除
                self.root.after(2000, self.reset_message_trap)
        
        elif trap["type"] == "fake_end" and self.game_state == "playing":
            # ダミーの記録表示（5秒後に元に戻す）
            if not self.active_traps["message"] and not self.active_traps["visual"]:
                # 両方のカテゴリを使用中にする
                self.active_traps["message"] = True
                self.active_traps["visual"] = True
                
                original_text = self.message_label.cget("text")
                original_bg = self.message_frame.cget("bg")
                original_button_state = self.stop_button.cget("state")
                
                # 偽の終了画面を作成
                fake_time = random.uniform(8.5, 11.5)
                fake_diff = abs(fake_time - 10)
                
                # ストップボタンを一時的に無効化
                self.stop_button.config(state=tk.DISABLED)
                
                # スタートボタンを一時的に有効化
                self.start_button.config(state=tk.NORMAL)
                
                # メッセージとスタイルを変更して偽の記録画面を表示
                self.message_label.config(
                    text=f"ゲーム終了！\nあなたの記録: {fake_time:.3f}秒\n10秒との差: {fake_diff:.3f}秒",
                    fg="#FFD700"
                )
                self.message_frame.config(bg="#2A2A2A")
                
                # 偽の評価メッセージを表示
                if fake_diff < 0.1:
                    fake_eval = "評価: 素晴らしい！ほぼ完璧な10秒感覚です！"
                elif fake_diff < 0.5:
                    fake_eval = "評価: すごい！かなり正確な時間感覚をお持ちです"
                elif fake_diff < 1.0:
                    fake_eval = "評価: なかなか良いですね！"
                elif fake_diff < 2.0:
                    fake_eval = "評価: もう少し練習しましょう"
                else:
                    fake_eval = "評価: トラップにはまってしまいましたね..."
                    
                # 結果ラベルに偽の評価を表示
                self.result_label.config(text=fake_eval, fg="#FF9500")
                
                # ゲームが終了していなければリセットする処理を予約
                def reset_if_playing():
                    # ゲームがまだプレイ中の場合のみリセット
                    if self.game_state == "playing":
                        self.message_label.config(
                            text="トラップでした！\nタイマーは継続中です。\n冷静に自分のペースを保ちましょう。", 
                            fg="#FFF"
                        )
                        self.message_frame.config(bg="#333")
                        self.result_label.config(text="", fg="#FFC107")
                        self.stop_button.config(state=tk.NORMAL)
                        
                        # さらに2秒後に通常のメッセージに戻す
                        self.root.after(2000, lambda: self.message_label.config(
                            text="10秒だと思ったら「ストップ」ボタンを押してください"
                        ) if self.game_state == "playing" else None)
                        
                        # トラップ状態をリセット
                        self.reset_fake_end_trap()
                
                # 5秒後にリセット
                self.root.after(5000, reset_if_playing)
        
        elif trap["type"] == "color_flash" and self.game_state == "playing":
            # 背景色フラッシュ
            if not self.active_traps["visual"]:
                self.active_traps["visual"] = True
                original_bg = self.message_frame.cget("bg")
                
                # 背景色を変更
                self.message_frame.config(bg=trap["color"])
                self.message_label.config(text="！！！")
                
                # 0.3秒後に元に戻す
                self.root.after(300, lambda: self.message_frame.config(bg="#333") if self.game_state == "playing" else None)
                self.root.after(300, lambda: self.message_label.config(text="10秒だと思ったら「ストップ」ボタンを押してください") if self.game_state == "playing" else None)
                
                # 少し間を置いてからトラップ状態を解除
                self.root.after(1000, self.reset_visual_trap)
        
        elif trap["type"] == "timer_jump" and self.game_state == "playing":
            # 偽タイマーを一瞬表示
            if not self.active_traps["timer"] and not self.show_fake_timer:
                self.active_traps["timer"] = True
                
                # 偽タイマーを表示
                self.timer_label.config(text=f"{trap['time']:.1f}", fg="#FF3300")
                
                # 0.5秒後に非表示にし、トラップ状態を解除
                self.root.after(500, lambda: self.timer_label.config(text="") if self.game_state == "playing" else None)
                self.root.after(1000, self.reset_timer_trap)
        
        elif trap["type"] == "system_error" and self.game_state == "playing":
            # システムエラー風メッセージ
            if not self.active_traps["system"] and not self.active_traps["message"]:
                self.active_traps["system"] = True
                self.active_traps["message"] = True
                
                original_text = self.message_label.cget("text")
                original_fg = self.message_label.cget("fg")
                
                # エラーメッセージを表示
                self.message_label.config(text=trap["message"], fg="#FF5555")
                
                # 2秒後に元に戻す、ただしゲームが終了していなければ
                self.root.after(2000, lambda: self.message_label.config(text="エラーから回復しました。計測を続けています...", fg="#00FF00") if self.game_state == "playing" else None)
                self.root.after(3500, lambda: self.message_label.config(text="10秒だと思ったら「ストップ」ボタンを押してください", fg="#FFF") if self.game_state == "playing" else None)
                
                # トラップ状態を解除
                self.root.after(4000, self.reset_system_trap)
    
    def reset_message_trap(self):
        """メッセージトラップの状態をリセットする"""
        self.active_traps["message"] = False
    
    def reset_visual_trap(self):
        """視覚的トラップの状態をリセットする"""
        self.active_traps["visual"] = False
    
    def reset_timer_trap(self):
        """タイマートラップの状態をリセットする"""
        self.active_traps["timer"] = False
    
    def reset_system_trap(self):
        """システムトラップの状態をリセットする"""
        self.active_traps["system"] = False
        self.active_traps["message"] = False
    
    def reset_fake_end_trap(self):
        """偽終了トラップの状態をリセットする"""
        self.active_traps["message"] = False
        self.active_traps["visual"] = False
# メインプログラム実行部分
if __name__ == "__main__":
    root = tk.Tk()
    app = TenSecondTrapGame(root)
    root.mainloop()