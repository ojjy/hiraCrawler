# hiraCrawler

1. 목적: 공공데이터포털에서 데이터를 가져오려고 하는데 넣어야할 파라미터가 많아 복잡도가 높아지거나 진료행위와 같이 데이터가 없을때 건강보험심사평가원(심평원)에서 운영하는 보건의료빅데이터시스템에서 직접 엑셀파일 다운받아 직접 데이터베이스에 넣는 식으로 데이터를 수집한다. 이때 일일이 엑셀파일 다운로드 받기 위한 크롤러이다.


3. chrome driver 사용자별로 chrome version에 맞게 다운 받아 프로젝트 폴더에 넣는다.
https://chromedriver.chromium.org/downloads


2. 크롤링하고자 하는 서비스 선택 및 실행
olapDiagBhvinfo.py는 진료행위
olapGnlInfo.py는 성분사용실적


References
https://opendata.hira.or.kr/
https://github.com/code-sonya/crawling
