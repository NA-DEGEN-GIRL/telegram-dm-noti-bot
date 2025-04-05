### README.md

## 프로젝트 개요

이 프로젝트는 사용자에게 도착하는 직접 메시지를 알림으로 전환하여 텔레그램의 기본 알림을 대체하는 데 목적이 있습니다. 사용자가 Telegram의 기본 알림을 비활성화한 상태에서도 중요한 개인 메시지를 빠짐없이 인지할 수 있도록, 별도의 봇을 통해 즉시 알림을 받도록 설계되었습니다. 이 프로그램은 개인 메시지가 수신되었을 때 지정된 관리자의 텔레그램 계정으로 알림을 즉각적으로 전송하여 메시지를 더 효과적으로 관리할 수 있도록 도와줍니다.

## 파일 설명

- **copy.key_tg.py**: 텔레그램 API 키 및 봇의 설정이 포함된 파일입니다. API ID, API Hash, 봇 토큰, 관리자 ID 등 필요한 설정이 담겨 있습니다. 파일명을 `key_tg.py`로 변경하여 사용하세요.
  
- **dm_noti_bot.py**: 텔레그램으로부터 메시지를 수신하고 알림을 보내는 봇의 메인 코드입니다. 이 파일은 TDLib와 Python의 asyncio를 이용해 메시지를 비동기적으로 처리합니다.

## 기능 설명

- **메시지 수신 및 알림 전송**: 각 개인 채팅에서 도착하는 메시지 중 읽지 않은 메시지를 검출하여, 관리자로 지정된 사용자에게 알림을 전달합니다.
- **비동기 메시지 처리 및 로깅 기능**: asyncio를 활용한 비동기 메시지 처리와 더불어, 프로그램 실행 중 중요한 이벤트와 에러 내용을 콘솔 및 로그 파일에 기록합니다.

## 요구 사항

- Python 3.7 이상
- Telegram API 키 및 TDLib 설치 필요
- 시스템 환경 설정에서 TDLib 설치 경로를 정확히 지정하여 사용해야 합니다 (`tdjson_path` 확인 필요)

## 설치 및 실행

1. **의존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```

2. **TDLib 설치**:
   [TDLib GitHub 저장소](https://github.com/tdlib/td)에서 소스 코드를 빌드하고 설치하세요. 운영체제별 빌드 방법은 [여기](https://tdlib.github.io/td/build.html)에서 확인 가능합니다.

3. **설정 파일 업데이트**:
   `key_tg.py`에 개인 텔레그램 API 정보를 입력하여 설정 파일을 최신화합니다.

4. **봇 실행**:
   ```bash
   python dm_noti_bot.py
   ```

---

### README.md (English Version)

## Project Overview

This project is designed to transform direct messages received by users into alerts, thereby replacing the default Telegram notifications. It ensures that important private messages are never missed, even when users have disabled native Telegram notifications, by sending immediate alerts through a separate bot. The program facilitates effective message management by instantly forwarding notifications to a specified administrator's Telegram account whenever a personal message is received.

## File Descriptions

- **copy.key_tg.py**: Contains Telegram API keys and bot configuration settings, including API ID, API Hash, bot token, and administrator ID. Rename this file to `key_tg.py` for use.
  
- **dm_noti_bot.py**: The main code for the bot that receives messages from Telegram and sends notifications. It processes messages asynchronously using TDLib and Python's asyncio.

## Feature Descriptions

- **Message Reception and Alerting**: Detects and sends alerts for unread messages in individual chats, directing notifications to a specified administrator.
- **Asynchronous Message Processing and Logging**: Implements asynchronous message processing with asyncio, while logging crucial events and errors to both the console and a log file.

## Requirements

- Python 3.7+
- Telegram API keys and TDLib installation required
- Ensure the system's environment is configured to correctly point to the installed path of TDLib (`tdjson_path` must be verified)

## Installation and Execution

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install TDLib**:
   Build and install from the [TDLib GitHub repository](https://github.com/tdlib/td). Operating system-specific build instructions can be found [here](https://tdlib.github.io/td/build.html).

3. **Update Configuration File**:
   Enter your personal Telegram API information into `key_tg.py` to update the configuration file.

4. **Run the Bot**:
   ```bash
   python dm_noti_bot.py
   ```