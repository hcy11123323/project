"""Test GitHub login through AgentLoop."""

import os

from src.sdk import AgentLoop

TEST_USERNAME = os.getenv("GITHUB_USERNAME", "feitianduowen")
TEST_PASSWORD = os.getenv("GITHUB_PASSWORD", "xxxxxxxx")


def run_github_login():
    """Run GitHub login through the natural-language agent flow."""
    print("开始测试 GitHub 登录...")
    print(f"用户名: {TEST_USERNAME}")
    print(f"密码: {'*' * len(TEST_PASSWORD)}")

    with AgentLoop(headless=False) as agent:
        result = agent.run(
            f"使用用户名 {TEST_USERNAME} 和密码 {TEST_PASSWORD} 登录 GitHub"
        )
        print("\n=== 登录结果 ===")
        print(result.output)

        input("\n按回车继续查看登录后的页面...")

        result = agent.run("截图当前页面并保存为 github_logged_in.png")
        print(result.output)


if __name__ == "__main__":
    run_github_login()
