import random
import streamlit as st

# 設定網頁標題
st.set_page_config(page_title="我的 AI 遊戲基地", layout="centered")

# 8-bit 復古 CSS
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #020024 0%, #090979 35%, #00d4ff 100%);
        color: #f8f8f2;
        font-family: 'Press Start 2P', monospace;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Press Start 2P', monospace;
    }
    .stButton>button {
        background: #ff9f1c;
        color: #1a1a1d;
        border: 3px solid #f08a5d;
        border-radius: 0;
    }
    .stButton>button:hover {
        background: #f7b267;
    }
    .score-board {
        border: 2px dashed #6a4c93;
        padding: 10px;
        background: rgba(0,0,0,.4);
    }
    .special {
        color: #00ff9f;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 8-bit 生存挑戰：冷酷機器人模式")

# 遊戲參數
TARGET_SCORE = 100
MAX_HP = 100

if 'initialized' not in st.session_state or not st.session_state.get('initialized', False):
    st.session_state.hp = MAX_HP
    st.session_state.score = 0
    st.session_state.turn = 0
    st.session_state.scene = '基地啟動'
    st.session_state.easter_egg_found = False
    st.session_state.last_actions = []
    st.session_state.status_msg = '系統啟動：所有參數正常。'
    st.session_state.game_over = False
    st.session_state.win = False
    st.session_state.bgm = '正常'
    st.session_state.initialized = True

# AI 語氣提示
ai_prompt = "冷靜計算中... 以邏輯方式評估風險與報酬。"
if st.session_state.hp < MAX_HP * 0.3:
    ai_prompt = "警告：生命危急。儘速恢復或尋找補給。"

# 背景色視覺回饋
def get_bg_color():
    if st.session_state.game_over:
        return '#8b0000'
    if st.session_state.hp <= MAX_HP * 0.3:
        return '#550000'
    if st.session_state.score >= TARGET_SCORE:
        return '#004d00'
    if st.session_state.scene == '探索':
        return '#001a66'
    return '#050a30'

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {get_bg_color()};
        transition: background-color 0.6s ease;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# 遊戲邏輯

# 顯示狀態
st.markdown("### 遊戲狀態")
col1, col2, col3 = st.columns(3)
col1.markdown(f"<div class='score-board'>HP: <span class='special'>{st.session_state.hp}</span></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='score-board'>分數: <span class='special'>{st.session_state.score}</span></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='score-board'>場景: <span class='special'>{st.session_state.scene}</span></div>", unsafe_allow_html=True)

st.markdown(f"**AI 提示**: {ai_prompt}")
st.info(f"循環回合: {st.session_state.turn} | {st.session_state.status_msg}")

# 更詳細的遊戲說明
st.markdown('### 遊戲說明')
st.markdown(
    '''
    你是冷酷機器人，啟動於復古 8-bit 界面。目標：
    - 生存並在 100 分前不被摧毀
    - 透過「探索、修復、休息、探測」累積分數並管理 HP
    - 第7回合或特定行動序列可觸發隱藏彩蛋（可額外獲得分數）
    - 背景顏色會隨場景與生命值動態改變，並有 Emoji 效果提示當前緊張度

    操作方式：
    1. 點擊行動按鈕執行回合
    2. 觀察 AI 提示與狀態面板
    3. 若失敗或勝利，可點擊「重新啟動遊戲」重置
    '''
)

# Emoji 動畫效果 (簡易)
emoji_options = ['⚡️', '🚀', '🔧', '💾', '🛡️']
st.write(''.join([random.choice(emoji_options) for _ in range(8)]))

# 行動函式

def end_game(win=False):
    st.session_state.game_over = True
    st.session_state.win = win
    st.session_state.scene = '完成' if win else '終止'
    st.session_state.status_msg = '勝利！目標達成。' if win else '失敗：機體失效。'


def check_status():
    if st.session_state.hp <= 0:
        st.session_state.hp = 0
        end_game(False)
    elif st.session_state.score >= TARGET_SCORE:
        end_game(True)


def reset_game():
    st.session_state.hp = MAX_HP
    st.session_state.score = 0
    st.session_state.turn = 0
    st.session_state.scene = '基地啟動'
    st.session_state.easter_egg_found = False
    st.session_state.last_actions = []
    st.session_state.status_msg = '系統重置：開始新的生存挑戰。'
    st.session_state.game_over = False
    st.session_state.win = False
    st.session_state.bgm = '正常'


def update_easter_egg(action):
    st.session_state.last_actions.append(action)
    st.session_state.last_actions = st.session_state.last_actions[-7:]

    if not st.session_state.easter_egg_found:
        if st.session_state.turn == 7:
            st.session_state.easter_egg_found = True
            st.session_state.score += 15
            st.session_state.status_msg = '彩蛋觸發：你發現了秘密伺服器！+15分'
        elif st.session_state.last_actions == ['探索','修復','探測','探索','休息','探索','探索']:
            st.session_state.easter_egg_found = True
            st.session_state.score += 25
            st.session_state.status_msg = '彩蛋觸發：邏輯序列完成。+25分'


def action_explore():
    if st.session_state.game_over:
        return
    st.session_state.turn += 1
    st.session_state.scene = '探索'
    update_easter_egg('探索')

    event = random.randint(1, 100)
    if event <= 35:
        damage = random.randint(5, 20)
        st.session_state.hp -= damage
        st.session_state.status_msg = f'遇到敵人，損失 {damage} HP。'
    elif event <= 60:
        gain = random.randint(10, 20)
        st.session_state.score += gain
        st.session_state.status_msg = f'找到資料包，獲得 {gain} 分。'
    elif event <= 80:
        recovery = random.randint(8, 18)
        st.session_state.hp = min(st.session_state.hp + recovery, MAX_HP)
        st.session_state.status_msg = f'發現補給站，回復 {recovery} HP。'
    else:
        st.session_state.status_msg = '無事件。冷酷機器人冷靜分析中……'

    check_status()


def action_repair():
    if st.session_state.game_over:
        return
    st.session_state.turn += 1
    st.session_state.scene = '修復'
    update_easter_egg('修復')

    success = random.random() < 0.7
    if success:
        recovery = random.randint(12, 22)
        st.session_state.hp = min(st.session_state.hp + recovery, MAX_HP)
        st.session_state.status_msg = f'修復成功，回復 {recovery} HP。'
    else:
        st.session_state.status_msg = '修復失敗，機體運作不順。'

    check_status()


def action_rest():
    if st.session_state.game_over:
        return
    st.session_state.turn += 1
    st.session_state.scene = '休息'
    update_easter_egg('休息')

    recovery = random.randint(6, 15)
    st.session_state.hp = min(st.session_state.hp + recovery, MAX_HP)
    st.session_state.score = max(0, st.session_state.score - 3)
    st.session_state.status_msg = f'低耗能休息，回復 {recovery} HP，-3 分。'

    check_status()


def action_scan():
    if st.session_state.game_over:
        return
    st.session_state.turn += 1
    st.session_state.scene = '探測'
    update_easter_egg('探測')

    scan_score = random.randint(5, 15)
    st.session_state.score += scan_score
    has_special = random.random() < 0.25
    st.session_state.status_msg = f'探測成功，獲得 {scan_score} 分。' + (' 發現稀有資源！' if has_special else '')
    if has_special:
        st.session_state.score += 5

    check_status()

# 互動按鈕
st.markdown('### 行動選擇')
colA, colB, colC, colD = st.columns(4)
with colA:
    if st.button('探索'): action_explore()
with colB:
    if st.button('修復'): action_repair()
with colC:
    if st.button('休息'): action_rest()
with colD:
    if st.button('探測'): action_scan()

if st.button('重新啟動遊戲'):
    reset_game()

# 遊戲結局顯示
if st.session_state.game_over:
    if st.session_state.win:
        st.success('🎉 勝利：你已達成分數目標！冷酷機器人任務完成。')
    else:
        st.error('💀 失敗：機體瓦解，生存挑戰結束。')

    if st.session_state.easter_egg_found:
        st.balloons()
        st.markdown('✨ 彩蛋已觸發：你的探索方式解鎖了秘密結局。')
    else:
        st.warning('🔍 彩蛋尚未發現，繼續嘗試不同操作序列。')

    st.markdown('---')
    st.write('遊戲重新開始可保留歷史紀錄，或點擊「重新啟動遊戲」。')
else:
    st.write('繼續執行動作以提高分數或保護生命值。')

st.markdown('---')
st.markdown('### 設定說明')
st.markdown("""
- 目標分數：100
- 初始 HP：100
- 使用 st.session_state 管理 HP、分數、回合、場景、彩蛋觸發狀態
- 冷酷機器人個性提示語氣：邏輯、冷靜、計算風格
- 視覺回饋：背景色隨生命/場景變化、Emoji 動畫顯示
""")

