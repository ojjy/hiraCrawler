"""
http://opendata.hira.or.kr/op/opc/olapDiagBhvInfo.do
진료행위(검사/수술)통계
"""
import hiraCrawler
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
from pathlib import Path
import pandas as pd
import time


class olapDiagBhvInfo(object):
    def __init__(self, url, edicode, type_btn, dir, title):
        self.url = url
        self.edicode_list = edicode
        self.type_btn = type_btn
        self.dir = dir
        self.title = title

    def crawler(self):
        print(self.url, self.type_btn, self.title, self.dir)
        chromedriver = "./chromedriver"

        for code in self.edicode_list:
            driver = webdriver.Chrome(chromedriver)
            driver.get(self.url)

            # main
            try:
                main = driver.current_window_handle
                driver.find_element_by_xpath('//*[@id="searchPopup"]').click()

                # popup
                popup = driver.window_handles
                driver.switch_to.window(popup.pop())
                driver.implicitly_wait(30)

                try:
                    driver.find_element_by_xpath('//*[@id="searchWrd1"]').send_keys(code)
                except Exception as e:
                    print(f"ERROR : {e}")
                    current_folder = Path(__file__).parent
                    failed_folder = os.path.join(current_folder, "failed")
                    with open(failed_folder+f"\\{code}.txt", "w") as fp:
                        fp.write(code)

                # 진료행위명칭
                driver.find_element_by_css_selector('a[id="searchBtn1"]').send_keys("\n")
                driver.implicitly_wait(10)
                driver.find_element_by_xpath('//*[@id="tab1"]/section[2]/table/tbody/tr/td[2]/a').click()

                # 메인창으로
                # /html/body/section[1]/section[2]/div[1]/ul/li[4]
                driver.switch_to.window(main)
                driver.find_element_by_xpath(self.type_btn).click()

                #iframe
                iframe = driver.find_element_by_class_name('olapViewFrame')
                driver.switch_to.frame(iframe)

                try:
                    wait = WebDriverWait(driver, 10)
                    time.sleep(30)

                    # //*[@id="ext-gen1449"]/table/tbody/tr/td/div[2]/table/tbody/tr/td/ul/li[2]/label/input
                    # radio = soup.find_all(name='radio_2')
                    radio = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#ext-gen1645 > table > tbody > tr > td > div:nth-child(2) > table > tbody > tr > td > ul > li:nth-child(2) > label > input[type="radio"]')))
                    radio = driver.find_element_by_css_selector('#ext-gen1645 > table > tbody > tr > td > div:nth-child(2) > table > tbody > tr > td > ul > li:nth-child(2) > label > input[type="radio"]')
                    driver.execute_script("arguments[0].click();", radio)

                    # driver.execute_script("arguments[0].click();", radio)
                    time.sleep(10)

                    ### 검색 시작 날짜 선택
                    from_date = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ext-gen1645']/table/tbody/tr/td/div[4]/div/input[1]")))
                    from_date.click()

                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    # ## 정규표현식으로 id 찾기 (monthpicker 값이 페이지 로드 마다 계속해서 바뀜)
                    mpid = soup.find_all(id=lambda x: x and x.startswith('monthpicker_'))
                    # print(mpid[0].attrs['id'])
                    # print(mpid[1].attrs['id'])
                    time.sleep(10)

                    ## 달력에서 년도 선택
                    # //*[@id="monthpicker_03292706759513271"]/div/select/option[9]
                    from_year_xpath = f"//*[@id='{mpid[0].attrs['id']}']/div/select/option[9]"
                    from_year = wait.until(EC.visibility_of_element_located((By.XPATH, from_year_xpath)))
                    from_year.click()

                    ## 달력에서 월 선택
                    from_month_xpath = f"//*[@id='{mpid[0].attrs['id']}']/table/tbody/tr[1]/td[1]"
                    from_month = wait.until(EC.visibility_of_element_located((By.XPATH, from_month_xpath)))
                    from_month.click()
                    time.sleep(10)

                    ### 검색 끝 날짜 선택
                    to_date = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ext-gen1645']/table/tbody/tr/td/div[4]/div/input[2]")))
                    to_date.click()

                    # ## 달력에서 년도 선택
                    # //*[@id="monthpicker_001981359078156262"]/div/select/option[11]
                    to_year_xpath = f"//*[@id='{mpid[1].attrs['id']}']/div/select/option[11]"
                    to_year = wait.until(EC.visibility_of_element_located((By.XPATH, to_year_xpath)))
                    to_year.click()

                    ## 달력에서 월 선택
                    # //*[@id="monthpicker_001981359078156262"]/table/tbody/tr[4]/td[3]
                    to_month_xpath = f"//*[@id='{mpid[1].attrs['id']}']/table/tbody/tr[4]/td[3]"
                    to_month = wait.until(EC.visibility_of_element_located((By.XPATH, to_month_xpath)))
                    to_month.click()
                    time.sleep(10)

                    ## 조회 버튼
                    search_btn = driver.find_element_by_class_name("dt-btn-search")
                    driver.execute_script("arguments[0].click();", search_btn)
                    driver.implicitly_wait(30)
                    ## 데이터가 로드될 때 까지 기다리기
                    try:
                        print("try")
                        datagrid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#panel-1184-body > div.dock_main > div.dock_inner div.m-datagrid-cell')))
                        time.sleep(10)

                    ## 조회된 데이터가 없는 경우
                    except Exception as e:
                        print("조회된 데이터가 없는 경우 except")
                        print(e)
                        base_dir = Path(__file__).parent
                        failpath = os.path.join(base_dir, 'failed')
                        with open(f'{failpath}\\{code}.txt', 'w') as f:
                            f.write(f'{code}')
                            driver.close()
                        continue

                    print("excel downloads")
                    download_excel = driver.find_element_by_xpath('//*[@id="panel-1184-body"]/div[2]/div[1]/div[1]/div[2]/div[1]')
                    driver.execute_script("arguments[0].click();", download_excel)
                    time.sleep(10)
                    driver.close()

                except Exception as e:
                    base_dir = Path(__file__).parent
                    failpath = f"{os.path.join(base_dir, 'failed')}/{code}.txt"
                    print(failpath)
                    with open(f'{failpath}', 'w') as f:
                        f.write(f'{code}')
                    driver.close()
                    print(e)

            except Exception as e:
                base_dir = Path(__file__).parent
                failpath = os.path.join(base_dir, 'failed')
                with open(f'{failpath}/{code}.txt', 'w') as f:
                    f.write(f'{code}')
                driver.close()
                print(e)


if __name__ == "__main__":
    hosp_type = '/html/body/section[1]/section[2]/div[1]/ul/li[4]'
    title = '요양기관종별'
    download_dir = os.path.join(os.getcwd(), "downloads")
    url = 'http://opendata.hira.or.kr/op/opc/olapDiagBhvInfo.do'
    # print(download_dir)
    excel_filepath = f"{os.path.join(os.getcwd(), 'edicode')}/edicode.xlsx"
    df = pd.read_excel(excel_filepath)
    # print(df)
    edicode_df = df['EDICODE']
    print(edicode_df)

    # Call constructor
    Bhvinfo_crawler = olapDiagBhvInfo(url=url,
                                    edicode=edicode_df,
                                    type_btn=hosp_type,
                                    dir=download_dir,
                                    title=title)
    Bhvinfo_crawler.crawler()
