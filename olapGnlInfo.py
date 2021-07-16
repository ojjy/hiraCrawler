"""
http://opendata.hira.or.kr/op/opc/olapGnlInfo.do
성분사용실적
성분의 시군구별 요양기관종별
"""
import os.path
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def add_lst(code):
        global failed_lst
        failed_lst.append(code)

class olapGnlInfoCrawler(object):
    def __init__(self, url, gnlNmCd_list, data_btn ,directory , by):
        self.url = url
        self.gnlNmCd_list = gnlNmCd_list
        self.data_btn = data_btn
        self.directory = directory
        self.by = by


    def crawl_data(self):
        url = 'http://opendata.hira.or.kr/op/opc/olapGnlInfo.do'
        chromedriver = './chromedriver'
        driver = webdriver.Chrome(chromedriver)
        driver.get(url)
        for gnlNmCd in self.gnlNmCd_list:
            try:
                driver.get(url)
                # main : 메인 창
                main = driver.current_window_handle
                driver.find_element_by_xpath('//*[@id="searchPopup"]').click()

                # popup : 팝업 창
                popup = driver.window_handles
                # driver.switch_to_window(popup.pop())
                driver.switch_to.window(popup.pop())
                driver.implicitly_wait(20)

                # 코드명으로 데이터 조회
                try:
                    driver.find_element_by_xpath('//*[@id="searchWrd1"]').send_keys(gnlNmCd)

                except Exception as e:
                    failed_lst.append(gnlNmCd)

                # 진료행위명칭 클릭
                driver.find_element_by_css_selector('a[id="searchBtn1"]').send_keys("\n")
                driver.implicitly_wait(3)
                driver.find_element_by_xpath('//*[@id="tab1"]/section[2]/table/tbody/tr/td[1]/a').click()

                # 메인 창으로 전환
                driver.switch_to.window(main)
                driver.find_element_by_xpath(self.data_btn).click()

                # iframe : iframe 영역
                iframe = driver.find_element_by_class_name('olapViewFrame')
                driver.switch_to.frame(iframe)
                # driver.switch_to.frame
                driver.implicitly_wait(20)


                #iframe
                try:
                    wait = WebDriverWait(driver, 10)
                    driver.implicitly_wait(10)

                    ### 검색 시작 날짜 선택
                    from_date = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ext-gen1169']/table/tbody/tr[1]/td/div[2]/div/input[1]")))
                    from_date.click()

                    # ## 정규표현식으로 id 찾기 (monthpicker 값이 페이지 로드 마다 계속해서 바뀜)
                    html = driver.page_source
                    soup = BeautifulSoup(html, 'html.parser')
                    mpid = soup.find_all(id=lambda x: x and x.startswith('monthpicker_'))
                    print(mpid[0].attrs['id'])
                    print(mpid[1].attrs['id'])

                    ## 달력에서 년도 선택
                    # //*[@id="monthpicker_04246456700999232"]/div/select/option[3]
                    from_year_xpath = f"//*[@id='{mpid[0].attrs['id']}']/div/select/option[3]"
                    from_year = wait.until(EC.visibility_of_element_located((By.XPATH, from_year_xpath)))
                    from_year.click()

                    ## 달력에서 월 선택
                    from_month_xpath = f"//*[@id='{mpid[0].attrs['id']}']/table/tbody/tr[1]/td[1]"
                    from_month = wait.until(EC.visibility_of_element_located((By.XPATH, from_month_xpath)))
                    from_month.click()
                    driver.implicitly_wait(10)

                    # #ext-gen1169 > table > tbody > tr:nth-child(1) > td > div:nth-child(2) > div > input:nth-child(4)
                    # //*[@id="ext-gen1169"]/table/tbody/tr[1]/td/div[2]/div/input[2]
                    ### 검색 끝 날짜 선택
                    to_date = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ext-gen1169']/table/tbody/tr[1]/td/div[2]/div/input[2]")))
                    to_date.click()
                    driver.implicitly_wait(10)

                    # ## 달력에서 년도 선택
                    # //*[@id="monthpicker_022440829795341255"]/div/select/option[5]
                    to_year_xpath = f"//*[@id='{mpid[1].attrs['id']}']/div/select/option[5]"
                    to_year = wait.until(EC.visibility_of_element_located((By.XPATH, to_year_xpath)))
                    to_year.click()

                    ## 달력에서 월 선택
                    # //*[@id="monthpicker_001981359078156262"]/table/tbody/tr[4]/td[3]
                    # //*[@id="monthpicker_022440829795341255"]/table/tbody/tr[4]/td[3]
                    # //*[@id="monthpicker_0299678668066261"]/table/tbody/tr[4]/td[3]
                    to_month_xpath = f"//*[@id='{mpid[1].attrs['id']}']/table/tbody/tr[4]/td[3]"
                    to_month = wait.until(EC.visibility_of_element_located((By.XPATH, to_month_xpath)))
                    to_month.click()

                    driver.implicitly_wait(10)
                    # 서울 //*[@id="ext-gen1169"]/table/tbody/tr[1]/td/div[4]/select/option[2]
                    # 부산 //*[@id="ext-gen1169"]/table/tbody/tr[1]/td/div[4]/select/option[3]
                    # 제주 //*[@id="ext-gen1169"]/table/tbody/tr[1]/td/div[4]/select/option[17]
                    # 세종 //*[@id="ext-gen1169"]/table/tbody/tr[1]/td/div[4]/select/option[18]
                    for sido_num in range(2, 19):
                        sidocode_xpath = f'//*[@id="ext-gen1169"]/table/tbody/tr[1]/td/div[4]/select/option[{sido_num}]'
                        sidocode = wait.until(EC.visibility_of_element_located((By.XPATH, sidocode_xpath)))
                        sidocode.click()

                        ## 조제, 처방구분
                        # //*[@id="ext-gen1169"]/table/tbody/tr[3]/td/div[2]/table/tbody/tr/td/ul/li[2]/label/input
                        # //*[@id="ext-gen1169"]/table/tbody/tr[3]/td/div[2]/table/tbody/tr/td/ul/li[2]/label/input
                        # //*[@id="ext-gen1169"]/table/tbody/tr[3]/td/div[2]/table/tbody/tr/td/ul/li[1]/label/input
                        # //*[@id="ext-gen1169"]/table/tbody/tr[3]/td/div[2]/table/tbody/tr/td/ul/li[2]/label/input
                        radio = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="ext-gen1169"]/table/tbody/tr[3]/td/div[2]/table/tbody/tr/td/ul/li[2]/label/input')))
                        radio = driver.find_element_by_xpath('//*[@id="ext-gen1169"]/table/tbody/tr[3]/td/div[2]/table/tbody/tr/td/ul/li[2]/label/input')
                        driver.execute_script("arguments[0].click();", radio)


                        ## 조회 버튼
                        search_btn = driver.find_element_by_class_name("dt-btn-search")
                        driver.execute_script("arguments[0].click();", search_btn)
                        driver.implicitly_wait(30)



                    #     ## 데이터가 로드될 때 까지 기다리기
                        try:
                            print("try")
                    # //*[@id="panel-1023-body"]/div[1]
                    # //*[@id="panel-1023-body"]/div[1]/div[1]
                    # panel-1023-body > div:nth-child(1) > div.dock_inner

                            datagrid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#panel-1023-body > div.dock_main > div.dock_inner div.m-datagrid-cell')))
                            driver.implicitly_wait(20)
                        ## 조회된 데이터가 없는 경우
                        except Exception as e:
                            print("조회된 데이터가 없는 경우 except")
                            print(e)
                            # driver.close()
                            continue

                        ## 엑셀파일 다운로드
                        # download_excel : 엑셀 다운로드 하는 버튼

                        print("excel downloads")
                        download_excel = driver.find_element_by_xpath('//*[@id="panel-1023-body"]/div[1]/div[1]/div[1]/div[2]/div[1]')
                        driver.execute_script("arguments[0].click();", download_excel)

                        ## 엑셀파일이 다운로드될 때 까지 기다리기
                        print ('''Downloading file....{}'''.format(gnlNmCd))
                        time.sleep(5)

                        ## 한 주상병코드 크롤링 완료
                        driver.implicitly_wait(10)
                        continue
                except Exception as e:
                    print (e)
                    # driver.close()
                    continue
            except Exception as e:
                continue
                # driver.close()




if __name__ == "__main__":
    # institution_btn : 요양기관종별 , location_btn : 요양기관소재지별 , directory : csv 파일 다운로드 되는 위치 (수정 필요)
    # body > section.container > section:nth-child(4) > div.st-tab-wrap.st > ul > li.olap-tab2.on > a
    # /html/body/section[1]/section[2]/div[1]/ul/li[2]/a
    institution_btn = '/html/body/section[1]/section[2]/div[1]/ul/li[2]'
    by_institution = '1_성분의시군구별요양기관종별'
    url = 'http://opendata.hira.or.kr/op/opc/olapGnlInfo.do'
    directory = os.path.join(os.getcwd(), 'downloads')
    print(directory)
    # directory = 'C:\\Users\\sm\\Downloads\\'

    # mdfeeCd_lst : 진료행위 코드 리스트
    df = pd.read_excel('csv_file/주성분코드.xlsx')
    print(df)
    gnlNmCd_list = df['주성분코드']

    # url, md_code, data_btn , count , directory , by):
    ## crawler_ins1 : 요양기관종별 데이터 크롤링
    print ('crawling Data ..............')
    crawler_ins1 = olapGnlInfoCrawler(url, gnlNmCd_list, institution_btn, directory , by_institution)
    # crawler_ins1 = OpendataCrawler(url, mdfeeCd_lst, location_btn, directory , by_location)
    crawler_ins1.crawl_data()