import streamlit as st
import sqlite3
import random

# ------------------- 初始化数据库 -------------------
conn = sqlite3.connect("group_assign.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
""")
conn.commit()

# ------------------- 分组设置 -------------------
GROUPS = {
    "哥斯拉战队 🐲": [],
    "龙猫部落 🍃": [],
    "蚂蚁联盟 🐜": [],
    "独角兽骑士团 🌟": []
}
MAX_PARTICIPANTS = 30

# ------------------- 学生端输入 -------------------
st.title("🪐 萌宇星球 · 随机分组器")

name = st.text_input("请输入你的名字：")

if st.button("提交"):
    cursor.execute("SELECT COUNT(*) FROM participants")
    count = cursor.fetchone()[0]

    if count >= MAX_PARTICIPANTS:
        st.warning("人数已满，不能再提交了～")
    elif name.strip() == "":
        st.warning("名字不能为空！")
    else:
        cursor.execute("INSERT INTO participants (name) VALUES (?)", (name.strip(),))
        conn.commit()
        st.success("提交成功，等待老师点击生成分组！")

# ------------------- 教师端操作 -------------------
st.markdown("---")
st.header("👩‍🏫 教师控制台")

if st.button("🎲 生成随机分组"):
    cursor.execute("SELECT name FROM participants")
    names = [row[0] for row in cursor.fetchall()]
    random.shuffle(names)

    group_list = list(GROUPS.keys())
    assignments = {g: [] for g in group_list}

    for i, name in enumerate(names):
        group = group_list[i % len(group_list)]
        assignments[group].append(name)

    st.success("✅ 分组已生成！")

    for group, members in assignments.items():
        st.subheader(f"{group}（{len(members)}人）")
        st.markdown("、".join(members))

if st.button("🔄 重置所有数据"):
    cursor.execute("DELETE FROM participants")
    conn.commit()
    st.warning("已清空所有数据，可重新开始分组啦！")
