import streamlit as st
import sqlite3
import random

# ---------------- 初始化数据库 ----------------
conn = sqlite3.connect("group_assign_final.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        group_name TEXT
    )
""")
conn.commit()

# ---------------- 分组配置 ----------------
GROUP_NAMES = ["哥斯拉战队 🐲", "龙猫部落 🍃", "蚂蚁联盟 🐜", "独角兽骑士团 🌟"]
MAX_PER_GROUP = 8
MAX_TOTAL = MAX_PER_GROUP * len(GROUP_NAMES)

# ---------------- 学生端界面 ----------------
st.title("🪐 萌宇星球 · 随机分组器")
name = st.text_input("请输入你的名字：")

if st.button("提交"):
    if not name.strip():
        st.warning("名字不能为空！")
    else:
        cursor.execute("SELECT COUNT(*) FROM participants")
        count = cursor.fetchone()[0]

        if count >= MAX_TOTAL:
            st.error("❌ 人数已满，不能再提交了。")
        else:
            # 检查是否已提交
            cursor.execute("SELECT * FROM participants WHERE name = ?", (name.strip(),))
            if cursor.fetchone():
                st.info("你已经提交过了，请等待老师展示分组结果～")
            else:
                # 统计每组人数
                cursor.execute("SELECT group_name, COUNT(*) FROM participants GROUP BY group_name")
                group_counts = {g: 0 for g in GROUP_NAMES}
                for g, c in cursor.fetchall():
                    group_counts[g] = c

                # 找出还有空位的组
                available_groups = [g for g, c in group_counts.items() if c < MAX_PER_GROUP]
                if not available_groups:
                    st.error("❌ 所有组都已满！")
                else:
                    assigned_group = random.choice(available_groups)
                    cursor.execute("INSERT INTO participants (name, group_name) VALUES (?, ?)", (name.strip(), assigned_group))
                    conn.commit()
                    st.success(f"提交成功，你被分到【{assigned_group}】")

# ---------------- 教师控制台 ----------------
st.markdown("---")
st.header("👩‍🏫 教师控制台")

# 展示分组
if st.button("📋 展示当前分组"):
    cursor.execute("SELECT name, group_name FROM participants")
    data = cursor.fetchall()
    if not data:
        st.info("还没有人提交哦～")
    else:
        grouped = {g: [] for g in GROUP_NAMES}
        for name, g in data:
            grouped[g].append(name)

        for g in GROUP_NAMES:
            st.subheader(f"{g}（{len(grouped[g])}人）")
            st.markdown("、".join(grouped[g]) if grouped[g] else "（暂无成员）")

# 重新打乱
if st.button("🔀 重新随机分组"):
    cursor.execute("SELECT name FROM participants")
    all_names = [row[0] for row in cursor.fetchall()]
    random.shuffle(all_names)
    new_assignments = []

    for i, name in enumerate(all_names):
        group = GROUP_NAMES[i % len(GROUP_NAMES)]
        new_assignments.append((group, name))

    for group, name in new_assignments:
        cursor.execute("UPDATE participants SET group_name = ? WHERE name = ?", (group, name))
    conn.commit()
    st.success("✅ 分组已重新打乱！请点击上方按钮查看新分组")

# 清空数据
if st.button("🗑️ 重置所有数据"):
    cursor.execute("DELETE FROM participants")
    conn.commit()
    st.warning("所有数据已清空，现在可以重新开始分组啦～")
