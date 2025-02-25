import pickle
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options


def parseNumber(name: str) -> str:
    num = re.sub("[^0-9]", "", name)
    return num[:4:] + "-" + num[4:8:]


def parseFaculty(fac: str) -> str:
    if "/" in fac:
        return fac[fac.find("/") + 1::]
    return fac


def parsePrerequisites(courseInfo: WebElement) -> str:
    text = courseInfo.text
    number = text[:9:]
    name = text[9::].strip()
    return name + "\n" + number


def scrapePrerequisites() -> list[str]:
    preCourses = browser.find_elements(By.XPATH, "//tr[td[@style='width:75px']]")
    result: list[str] = []
    for i in range(len(preCourses)):
        result.append(parsePrerequisites(preCourses[i]))
    return result


def openPrerequisitesWindow(preButton: WebElement) -> list[str]:
    preButton.click()

    windows = browser.window_handles
    main_window = browser.current_window_handle

    for window in windows:
        if window != main_window:
            browser.switch_to.window(window)
            break

    # print("Now on site B:", browser.current_url)

    result = scrapePrerequisites()

    browser.close()
    browser.switch_to.window(main_window)
    # print("Back to site A:", browser.current_url)

    return result


def parseCourses(data: list[list[WebElement]], courses: dict[str: list[str]]) -> None:
    for i in range(len(data)):
        Number: str = parseNumber(data[i][0].find_elements(By.TAG_NAME, "td")[0].text.strip())
        Name: str = data[i][0].find_elements(By.TAG_NAME, "td")[1].text.strip()
        node: str = Name + "\n" + Number

        faculty = data[i][-1]
        data[i] = data[i][:-1]
        print(node, faculty, sep="\n", end="\n\n")

        prerequisites = []
        if len(data[i]) == 2:
            prerequisites = openPrerequisitesWindow(data[i][1])

        if node not in courses:
            courses[node] = [faculty]

        seen = set(courses[node])
        for item in prerequisites:
            if item not in seen:
                courses[node].append(item)
                seen.add(item)


def seperateCourses(courses: dict[str: list[str]]) -> None:
    coursesList = browser.find_elements(By.TAG_NAME, "tbody")[1]
    dataList = coursesList.find_elements(By.XPATH, "//tr[@class='listtdbld'] | //a[@title='דרישות קדם']")

    dataStorage: list[list[WebElement]] = []
    tmp: list = []
    for i in range(len(dataList)):
        if 'listtdbld' in dataList[i].get_attribute("class") and i != 0:
            next_element = dataList[i].find_element(By.XPATH, "following-sibling::*[1]")
            faculty = parseFaculty(next_element.text)
            tmp.append(faculty)
            dataStorage.append(tmp)
            tmp = []
        if i == 174:
            pass
        tmp.append(dataList[i])

    if 'listtdbld' in dataList[len(dataList) - 1].get_attribute("class"):
        next_element = dataList[len(dataList) - 1].find_element(By.XPATH, "following-sibling::*[1]")
        faculty = parseFaculty(next_element.text)
        tmp.append(faculty)
    else:
        next_element = dataList[len(dataList) - 2].find_element(By.XPATH, "following-sibling::*[1]")
        faculty = parseFaculty(next_element.text)
        tmp.append(faculty)
    dataStorage.append(tmp)

    parseCourses(dataStorage, courses)


def copyCourses(courses: dict[str: list[str]]) -> None:
    while True:
        seperateCourses(courses)
        try:
            nextB = browser.find_element(By.ID, "next")
        except:
            return
        nextB.click()


def main():
    courses: dict[str: list[str]] = dict()
    browser.find_element(By.ID, "lstDep6").find_elements(By.TAG_NAME, "option")[1].click()
    browser.find_element(By.ID, "search1").click()
    copyCourses(courses)

    print(courses)
    with open("prerequisites.pkl", "wb") as file:
        pickle.dump(courses, file)


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # for Chrome >= 109

    browser = webdriver.Chrome(options=chrome_options)
    browser.get('https://www.ims.tau.ac.il/tal/kr/Search_P.aspx')
    # browser.save_screenshot("screenshot.png")
    main()
    browser.close()
