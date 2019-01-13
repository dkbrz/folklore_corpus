from flask_table import Table, Col, NestedTableCol, LinkCol
INFORMATOR_LINK = '/informator/{}'

class InformatorSubTable(Table):
    classes = ['sub-table']
    code = Col('Код')
    gender = Col('Гендер')
    birth_year = Col('Год рождения')
    #current_region = Col('')

class KeywordsSubTable(Table):
    classes = ['sub-table']
    word = Col('Ключевое слово', th_html_attrs={'hidden':'True'})

class QuestionsSubTable(Table):
    classes = ['sub-table']
    question_list = Col('Лист')
    question_code = Col('Вопрос')

class MainSearchTable(Table):
    classes = ['large-table']
    id = Col('ID', th_html_attrs={'class':'large-th'})
    old_id = Col('Прежний ID', th_html_attrs={'class':'large-th'})
    #raw_text = LinkCol('текст', 'text/', url_kwargs=dict(id='id'), th_html_attrs={'class':'large-th'})
    year = Col('Год', th_html_attrs={'class':'large-th'})
    region = Col('Регион', th_html_attrs={'class':'large-th'})
    district = Col('Район', th_html_attrs={'class':'large-th'})
    village = Col('Населенный пункт', th_html_attrs={'class':'large-th'})
    genre = Col('Жанр', th_html_attrs={'class':'large-th'})
    informators = NestedTableCol('Инфоманты', InformatorSubTable, th_html_attrs={'class':'large-th'})
    questions = NestedTableCol('Вопросы', QuestionsSubTable, th_html_attrs={'class':'large-th'})
    keywords = Col('keywords', th_html_attrs={'class':'large-th'})
    #keywords = NestedTableCol('Ключевые слова', KeywordsSubTable, th_html_attrs={'class':'large-th'})

class TextForTable:
    def __init__(self, object):
        self.id = object.id
        self.old_id = object.old_id
        self.year = object.year
        self.region = object.region
        self.district = object.district
        self.village = object.village
        self.informators = object.informators
        self.questions = object.questions
        self.questions = object.questions
        self.genre = object.genre
        self.keywords = ', '.join(sorted([keyword.word for keyword in object.keywords]))

class InformatorSubTableText:
    code = Col('Код')
    gender = Col('Гендер')
    birth_year = Col('Год рождения')
    current_region = Col('Регион проживания')
    current_district = Col('Район проживания')
    current_village = Col('Населенный пункт')
    birth_region = Col('Регион рождения')
    birth_district = Col('Район рождения')
    birth_village = Col('Место рождения')

