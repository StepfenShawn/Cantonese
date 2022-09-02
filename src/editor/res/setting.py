import xml.dom.minidom

class LangType():
    ENGLISH = "en"
    CHINESE = "cn"

class LanguageSetter(object):
    
    def __init__(self, type) -> None:
        self.type = type
        self.data = self.read()

    def read(self):
        if self.type == LangType.CHINESE:
            dom  = xml.dom.minidom.parse('res/languages/strings_cn.xml')
        elif self.type == LangType.ENGLISH:
            dom = xml.dom.minidom.parse('res/languages/strings.xml')
        data = {
                'openfile' : dom.getElementsByTagName('openfile')[0].firstChild.data,
                'openmorefile' : dom.getElementsByTagName('openmorefile')[0].firstChild.data,
                'change_font' : dom.getElementsByTagName('change_font')[0].firstChild.data,
                'change_color' : dom.getElementsByTagName('change_color')[0].firstChild.data,
                'save_file' : dom.getElementsByTagName('save_file')[0].firstChild.data,
                'set_page' : dom.getElementsByTagName('set_page')[0].firstChild.data,
                'print_file' : dom.getElementsByTagName('print_file')[0].firstChild.data,
                'clear_file' : dom.getElementsByTagName('clear_file')[0].firstChild.data,
                'run_file' : dom.getElementsByTagName('run_file')[0].firstChild.data,
                'exit_' : dom.getElementsByTagName('exit')[0].firstChild.data,
                'NodeMainName' : dom.getElementsByTagName('NodeMainName')[0].firstChild.data,
                'NodeOutputName' : dom.getElementsByTagName('NodeOutputName')[0].firstChild.data,
                'NodeVarName' :  dom.getElementsByTagName('NodeVarName')[0].firstChild.data
            }
        return data