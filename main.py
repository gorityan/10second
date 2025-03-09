import threading
import time
import random
import sys

# 終了フラグ（スレッド間で共有するグローバル変数）
game_over = False

# ランダムなトラップメッセージを生成する関数
def generate_trap_message():
    messages = [
        "3秒経過!",  # フェイクの経過時間
        "5秒経過!",
        "7秒経過!",
        "9秒経過!",
        "11秒経過!",
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

# トラップメッセージを表示するスレッド関数
def display_trap_messages():
    global game_over
    
    # ゲームが終了するまでループ
    while not game_over:
        # ランダムな待機時間（1〜3秒）
        wait_time = random.uniform(1.0, 3.0)
        time.sleep(wait_time)
        
        # ゲームが終了していなければメッセージを表示
        if not game_over:
            trap_message = generate_trap_message()
            print(f"\n{trap_message}")
            print("10秒だと思ったらEnterキーを押してください...", end="", flush=True)

# メイン関数
def main():
    global game_over
    
    print("===== 10秒トラップゲーム =====")
    print("ルール：")
    print("1. Enterキーを押すとタイマーがスタートします")
    print("2. ちょうど10秒経過したと思ったらもう一度Enterキーを押してください")
    print("3. 実際の経過時間がどれだけ10秒に近いかを競います")
    print("注意：途中で表示されるメッセージはあなたを惑わせるためのトラップです！")
    print("\nゲームを開始するにはEnterキーを押してください...")
    
    # ゲーム開始を待機
    input()
    
    print("\nタイマースタート!10秒だと思ったらEnterキーを押してください...", end="", flush=True)
    
    # 開始時間を記録
    start_time = time.time()
    
    # トラップメッセージを表示するスレッドを開始
    trap_thread = threading.Thread(target=display_trap_messages)
    trap_thread.daemon = True  # メインスレッドが終了したら自動的に終了
    trap_thread.start()
    
    # プレイヤーの入力を待機
    input()
    
    # 終了時間を記録し、ゲーム終了フラグをセット
    end_time = time.time()
    game_over = True
    
    # 経過時間を計算
    elapsed_time = end_time - start_time
    
    # 結果を表示
    print("\n\n===== ゲーム結果 =====")
    print(f"あなたの記録: {elapsed_time:.3f}秒")
    print(f"10秒との差: {abs(elapsed_time - 10):.3f}秒")
    
    # 評価を表示
    if abs(elapsed_time - 10) < 0.1:
        print("評価: 素晴らしい!ほぼ完璧な10秒感覚です!")
    elif abs(elapsed_time - 10) < 0.5:
        print("評価: すごい！かなり正確な時間感覚をお持ちです")
    elif abs(elapsed_time - 10) < 1.0:
        print("評価: なかなか良いですね！")
    elif abs(elapsed_time - 10) < 2.0:
        print("評価: もう少し練習しましょう")
    else:
        print("評価: トラップにはまってしまいましたね...")

# プログラムのエントリポイント
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+Cで終了した場合
        print("\n\nゲームを終了します")
        game_over = True
        sys.exit(0)