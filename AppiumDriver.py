#encoding:utf-8
'''
Created on Aug 6, 2013

@author: dfeng
'''

from selenium import webdriver
from Library import UIMapping as uimap
from MTDriver import MTElement,MTComponentType
import os,sys,time

class AppiumDriver(object):
    '''
    driver for Alert apps
    
    Two types of methods:
        1. Element locating methods.
        2. Action performing methods. Perform action on a certain element.
    '''
    
    def __init__(
                 self, 
                 mtdriver,
                 app, 
                 UDID,
                 appium_server="127.0.0.1:4723"
                 ):
        '''
        Need to assign the app path.
        '''
        self.mtdriver = mtdriver
        desired_caps = {}
        desired_caps['browserName'] = 'iOS'
        desired_caps['platform'] = 'Mac'
        desired_caps['platformName'] = 'iOS'
        desired_caps['deviceName'] = 'iPhone'
        desired_caps['newCommandTimeout'] = 60000
        desired_caps['autoAcceptAlerts'] = True #close location services popup window
        desired_caps['version'] = '7.1'
        desired_caps['udid'] = UDID
        desired_caps['app'] = app
        #desired_caps['app'] = '/Users/mxu/Documents/dfeng/UBASourceCode/UBA1.1.09/universal_badge_1.1.09/iOS/SingleBadge/DerivedData/Build/Products/Release-iphoneos/Usher.app' #not supported in real machine 
        #desired_caps['version'] = '6.1'
        #desired_caps['app'] = os.path.abspath(app_path)
        
        self.appium_server = appium_server
        self.desired_caps = desired_caps
        
        self.wd = webdriver.Remote('http://'+appium_server+'/wd/hub', desired_caps)
        self.default_implicitly_wait = 50
        self.wd.implicitly_wait(self.default_implicitly_wait)
        
        self.device_size = 0
    
        
    #----------------------------------------------------------------------------------------
    # methods for MTDriver
    #
    def open_link(self,link):
        MTElement(self,MTComponentType.Device,'*',link).OpenLink()
        
#     def wait_for(self, componentType, monkeyId, expectedValue=None, timeout=60, raiseIfTimeout=True):
#         return self.WaitFor(componentType, monkeyId, expectedValue, timeout, raiseIfTimeout)
    
    #----------------------------------------------------------------------------------------
    # Miscellaneous methods
    #
    def is_alert_present(self):
        try:
            self.wd.switch_to_alert().text
            return True
        except:
            return False
        
    def quit(self): 
        return self.wd.quit()
     
    def relaunch(self):
        self.wd = webdriver.Remote('http://'+self.appium_server+'/wd/hub', self.desired_caps)
        
        
    def get_device_resolution(self):
        if self.device_size == 0:
            self.device_size = self.wd.find_element_by_xpath(uimap.general.max_window).size
        return self.device_size
     
    def get_session_id(self):
        return self.wd.session_id
    
    #    
    def execute_script(self, script, args=None):
        return self.wd.execute_script(script, args)
        
    #----------------------------------------------------------------------------------------
    # find element by giving the UI map element
    #
    ''' FINDING ELEMENT METHODS '''
    
    def find_element(self, uimap_element, element_type=0):
        
        if element_type == 1 or uimap_element.find('//') == 0:
            # should be xpath element
            return self.find_element_by_xpath(uimap_element)
        
        elif element_type == 2:
            # find element by partial text
            return self.find_element_by_partial_text(uimap_element)

        else:
            # find by name
            return self.find_element_by_name(uimap_element)
        
    #     
    def find_element_by_name(self, name):
        return self.wd.find_element_by_name(name)

    #     
    def find_element_by_tag_name(self, name):
        return self.wd.find_element_by_tag_name(name)
        
    #
    def find_element_by_xpath(self, xpath):
        return self.wd.find_element_by_xpath(xpath)
    
    
    def find_element_by_partial_text(self, text, count = 1):
        '''
        Find an element by its partial text
        this function is with low efficiency.
        
        Parameters:
            text        : array of words
            count       : the number of the expected element  
            
        Return:
            the expected WebElement or None
        '''
        if not isinstance(text, list):
            text = [text]
            
        elements = self.wd.find_elements_by_tag_name(uimap.tag_names.label)
        temp = None
        for element in elements:
            f = True
            for s in text:
                if not s in element.text:
                    f = False
                    break
            if f:
                count -= 1
                if count == 0:
                    return element
                else:
                    temp = element
        return temp
    
    
    def loading_status(self):
        '''
        return boolean telling whether is still loading or not
        '''
        
        statusbar = self.wd.find_element_by_xpath('//window[2]/statusbar[1]')
        # get all elements on the status bar
        eles = statusbar.find_elements_by_xpath('*')
        # the loading element's name is "Network connection in progress"
        for ele in eles:
            #print ele.get_attribute('name')
            if "Network connection in progress" == ele.get_attribute('name'):
                return True
        
        try:
            self.wd.implicitly_wait(0.1)   
            eles = self.wd.find_elements_by_tag_name('activityIndicator')
            self.wd.implicitly_wait(30)
            return eles[0].is_displayed()
        except:
            self.wd.implicitly_wait(30)
            return False
        
    def wait_for_element_by_name(self, name, waitTime=30):
        '''
        wait for specific element
        '''
        self.wd.implicitly_wait(waitTime)   
        try:
            element = self.wd.find_element_by_name(name)  
            print "Element: %s found!"%name
            return True
        except:
            print "Element: %s not found! Time out!"%name
            return False
        finally:
            self.wd.implicitly_wait(self.default_implicitly_wait)
                    
    #----------------------------------------------------------------------------------------
    # execute actions by giving the UI map name
    #
    ''' ACTION METHODS '''
    
    # click element
    def click(self, uimap_element, element_type=0):
        t = str(type(uimap_element)).lower()
        if 'webelement' in t:
            element = uimap_element
        else:
            element = self.find_element(uimap_element, element_type)
        return element.click()
    
    def try_to_click(self, uimap_element, element_type=0):
        self.wd.implicitly_wait(1)  
        try:
            self.click(uimap_element, element_type)
        except:
            self.wd.implicitly_wait(30)
            return False

        self.wd.implicitly_wait(30)
        return True
    
    # send keys
    def send_keys(self, uimap_element, keys, element_type=0):
        t = str(type(uimap_element)).lower()
        if 'webelement' in t:
            element = uimap_element
        else:
            element = self.find_element(uimap_element, element_type)
        return element.send_keys(keys)
    
    # save screenshot as file. pic_name: the saved file path
    def get_screenshot_as_file(self, pic_name):
        return self.wd.get_screenshot_as_file(pic_name)
    
    # refresh the current view
    def refresh(self):
        self.return_to_top()
        return self.wd.execute_script("mobile: swipe", {"touchCount": 1 , "startX": 168, "startY": 105, "endX": 165, "endY": 326, "duration": 0.5 })
        while self.loading_status():
            time.sleep(0.5)
    
    def return_to_top(self):
        '''
        return to the top of list by clicking the status bar
        '''
        self.wd.find_element_by_xpath("//window[2]/statusbar[1]").click()
        
    def click_table_cell_by_index(self, index, tableid=0):
        tables = self.wd.find_elements_by_tag_name('tableView')
        cell = tables[tableid].find_elements_by_tag_name('tableCell')[index]
        cell.click()
        
    
    def move(self, direction, delta):
        '''
        Move function
        '''
        d = {'up' : [0, 1], 'down' : [0, -1],  'left' : [1, 0], 'right' : [-1, 0]}
        
        size = self.get_device_resolution()
        
        if delta <=1 :
            delta = int(size['height']*delta) if direction in ['up','down'] else int(size['width']*delta)
            
        cx = size['width'] / 2
        cy = size['height'] / 2 - 64
        
        h = min( delta, cx*2-10) if direction in ['left', 'right'] else min(delta, cy*2-10)
        
        while delta > 0 :
            
            hh = h/2
            param =  {
                  "touchCount" : 1,
                  "startX"     : cx + d[direction][0]*hh,
                  "endX"       : cx - d[direction][0]*hh,
                  "startY"     : cy + d[direction][1]*hh,
                  "endY"       : cy - d[direction][1]*hh,
                  "duration"   : max(0.5, 0.5*hh/200)
                  }
            self.wd.execute_script("mobile: swipe", param)
            delta -= h
            h = min(h, delta)
            time.sleep(0.5)
        return True
    
    
    def move_point_to_point(self, startp, endp):
        '''
        Move from one position to another position
        '''
        size = self.get_device_resolution()
        
        if startp[0]*startp[1] <= 1:
            startx = startp[0] * size['width']
            starty = startp[1] * size['height']
        
        if endp[0]*endp[1] <= 1:
            endx = endp[0] * size['width']
            endy = endp[1] * size['height']
             
        param = {
                  "touchCount" : 1,
                  "startX"     : startx,
                  "endX"       : endx,
                  "startY"     : starty,
                  "endY"       : endx,
                  "duration"   : 0.5
                  }
        self.wd.execute_script("mobile: swipe", param)
        
    
    def move_element_to_visible_area(self, element):
        '''
        # scroll the element to visible area
        # according to the location and size
        '''
        
        if element.is_displayed():
            return None
        
        location = element.location
        size = element.size
        device_size = self.get_device_resolution()

           
        if location['y'] > device_size['height']:
            delta = location['y'] - device_size['height'] + size['height'] + 20
            self.move('up', delta)

        if location['y'] < 0:
            delta = 40 - location['y']
            self.move('down', delta)
          
        if location['x'] > device_size['width']:
            delta = location['x'] - device_size['width'] + size['width'] + 20
            self.move('left', delta)
            
        if location['x'] < 0:
            delta = 20 - location['x']
            self.move('right', delta)
            
        return True      

    #----------------------------------------------------------------------------------------
    # execute actions by giving the UI map name
    #
    ''' UBA SPECIFIC METHODS '''
    def swipe_right(self):
        '''swipe from left to right'''
        self.execute_script("mobile: swipe", {"touchCount": 1 , "startX": 23, "startY": 308, "endX": 307, "endY": 315, "duration": 0.5 })

    def swipe_left(self):
        '''swipe from right to left'''
        self.execute_script("mobile: swipe", {"touchCount": 1 , "startX": 307, "startY": 315, "endX": 23, "endY": 308, "duration": 0.5 }) 
        
    def send_to_background_for_seconds(self, seconds):
        self.execute_script("mobile: background", {"seconds": seconds}) 
        
    def lock_device_for_seconds_and_unlock(self, seconds, unlock_pin=None):
        '''seconds: lock time
           unlock_pin: pin code to unlock the device, e.g. "1234" or ["1","2","3","4"]. None if you don't set the pin code.
        '''
        self.execute_script("mobile: lock", {"seconds": seconds}) 
        if unlock_pin:
            unlock_pin = unlock_pin.strip()
            for i in range(4):
                self.find_element_by_name(str(unlock_pin[i])).click()
    
    def login_badge(self, username, password):
        self.wd.find_element_by_xpath(uimap.textfield.username).send_keys(username)  #not stable using appium
        self.wd.find_element_by_tag_name(uimap.tag_type.password).send_keys(password) 
        #self.wd.find_element_by_xpath(uimap.textfield.password).send_keys(password) #not stable using appium
        #MTElement(self,MTComponentType.UITextField,'Username').EnterText(username)
        #MTElement(self,MTComponentType.UITextField,'Password').EnterText(password)
        self.wd.find_element_by_name("Confirm").click()
        #need wait for method
        Skip_button = MTElement(self,MTComponentType.UIButton,'Skip')
        if Skip_button.WaitFor(15):
            #Skip_button.tap()  #not work
            self.wd.find_element_by_name("Skip").click()


if __name__ == "__main__":
    if (len(sys.argv) < 3):
        print ("Please input app_path and appium_server!")
        print ("e.g. python start_session.py app_path appium_server")
        sys.exit()
    app_path = sys.argv[1]
    appium_server = sys.argv[2]
    
    app_driver = AppiumDriver(app_path, appium_server)
    session_id = app_driver.get_session_id()
    
    # Write session id to a file
    sessionId_file = open('sessionId.properties','w')
    sessionId_file.write('sessionId=%s\n'% session_id)
    sessionId_file.close()


