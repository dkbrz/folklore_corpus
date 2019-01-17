from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, select
from folklore_app.models import *
from folklore_app.tables import *
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

MAX_RESULT = 200

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost:3306/folklore_db'
    app.secret_key = 'yyjzqy9ffY'
    db.app = app
    db.init_app(app)
    return app

app = create_app()
#db.create_all()
#app.app_context().push()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=request.form.get('username')).one_or_none()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return render_template('login.html', message='{}, добро пожаловать!'.format(user.name))
        return render_template('login.html', message='Попробуйте снова!')
    else:
        return render_template('login.html', message='')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.form:
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        email = request.form.get('email')
        name = request.form.get('name')
        if User.query.filter_by(username=request.form.get('username')).one_or_none():
            return render_template('signup.html', message='Имя {} уже занято!'.format(username))
        else:
            new_user = User(username=username, password=password, email=email, role='basic', name=name)
            db.session.add(new_user)
            db.session.commit()
            return render_template('signup.html', message='{}, добро пожаловать!'.format(new_user.name))
    else:
        return render_template('signup.html', message='???')

@app.route("/database")
def database():
    selection = database_fields()
    
    return render_template('database.html', selection=selection)

@app.route("/text/<idx>")
def text(idx):
    text = Texts.query.filter_by(id=idx).one_or_none()
    collectors = ', '.join(sorted([collector.code for collector in text.collectors]))
    keywords = ', '.join(sorted([keyword.word for keyword in text.keywords]))
    video = text.video.split('\n')
    print (video)
    return render_template('text.html', textdata=text, collectors=collectors, keywords=keywords, video=video)

@app.route("/edit/<idx>")
@login_required
def edit(idx):
    text = Texts.query.filter_by(id=idx).one_or_none()
    other = {}
    other['collectors'] = [(collector.id, '{} | {}'.format(collector.id,collector.name),) for collector in text.collectors]
    seen_collectors = set(i[0] for i in other['collectors'])
    other['_collectors'] = [(collector.id, '{} | {}'.format(collector.id, collector.name),) for collector in Collectors.query.order_by('name').all()]
    other['keywords'] = [(keyword.id, keyword.word,) for keyword in text.keywords]
    other['_keywords'] = [(keyword.id, keyword.word,) for keyword in Keywords.query.order_by('word').all() if keyword.word not in other['keywords']]
    other['informators'] = [(informator.id, '{} | {} | {}'.format(informator.id, informator.name, informator.current_village),) for informator in text.informators]
    seen_informators = set(i[0] for i in other['informators'])
    other['_informators'] = [(informator.id, '{} | {} | {}'.format(informator.id, informator.name, informator.current_village),) for informator in Informators.query.order_by('current_village, name').all() if informator.id not in seen_informators]
    return render_template('edit.html', 
        textdata=text, 
        other=other)

@app.route("/text_edited", methods=['POST','GET'])
@login_required
def text_edited():
    if request.form:
        text = Texts.query.get(request.form.get('id', type=int))
        if request.form.get('submit', type=str) == 'Удалить':
            db.session.delete(text)
        else:
            text.old_id = request.form.get('old_id', type=str)
            text.year = request.form.get('year', type=int)
            text.region = request.form.get('region', type=str)
            text.district = request.form.get('district', type=str)
            text.village = request.form.get('village', type=str)
            text.address = request.form.get('address', type=str)
            text.genre = request.form.get('genre', type=str)
            text.raw_text = request.form.get('raw_text', type=str)
            
            informators = Informators.query.filter(Informators.id.in_(request.form.getlist('informators', type=int))).all()
            text.informators = informators
            collectors = Collectors.query.filter(Collectors.id.in_(request.form.getlist('collectors', type=int))).all()
            text.collectors = collectors
            keywords = Keywords.query.filter(Keywords.id.in_(request.form.getlist('keywords', type=int))).all()
            text.keywords = keywords
            #text.old_id = request.form.get('id', type=int)
            #text.old_id = request.form.get('id', type=int)
        db.session.commit()
        if request.form.get('submit', type=str) != 'Удалить':
            return redirect(url_for('text', idx = text.id))
        else:
            return redirect(url_for('database'))
    else:
        return redirect(url_for('database'))

@app.route("/add/text")
@login_required
def add():
    other = {}
    other['_collectors'] = [(collector.id, '{} | {}'.format(collector.id, collector.name),) for collector in Collectors.query.order_by('name').all()]
    other['_keywords'] = [(keyword.id, keyword.word,) for keyword in Keywords.query.order_by('word').all()]
    other['_informators'] = [(informator.id, '{} | {} | {}'.format(informator.id, informator.name, informator.current_village),) for informator in Informators.query.order_by('current_village, name').all()]
    return render_template('add_text.html', other=other)

@app.route("/text_added", methods=['POST','GET'])
@login_required
def text_added():
    if request.form:
        old_id = request.form.get('old_id', type=str)
        year = request.form.get('year', type=int)
        region = request.form.get('region', type=str)
        district = request.form.get('district', type=str)
        village = request.form.get('village', type=str)
        address = request.form.get('address', type=str)
        genre = request.form.get('genre', type=str)
        raw_text = request.form.get('raw_text', type=str)
        
        informators = Informators.query.filter(Informators.id.in_(request.form.getlist('informators', type=int))).all()
        collectors = Collectors.query.filter(Collectors.id.in_(request.form.getlist('collectors', type=int))).all()
        keywords = Keywords.query.filter(Keywords.id.in_(request.form.getlist('keywords', type=int))).all()
        text = Texts(
            old_id=old_id, year=year, 
            region=region, district=district, village=village, address=address, 
            genre=genre, 
            raw_text=raw_text,
            informators=informators, collectors=collectors, keywords=keywords)
        db.session.add(text)
        db.session.flush()
        db.session.refresh(text)
        db.session.commit()
        return redirect(url_for('text', idx = text.id))
    else:
        return redirect(url_for('database'))

@app.route("/add/collector", methods=['POST','GET'])
@login_required
def add_collector():
    if request.form:
        
        old_id = request.form.get('old_id', type=str)
        name = request.form.get('name', type=str)
        code = request.form.get('code', type=str)
        collector = Collectors(old_id=old_id, name=name, code=code)
        
        db.session.add(collector)
        db.commit()

        return redirect(url_for('collectors'))
    else:
        return render_template('add_collector.html')

@app.route("/edit/collector/<id_collector>", methods=['POST','GET'])
@login_required
def edit_collector(id_collector):
    if request.form:
        print (request.form)
        person = Collectors.query.get(request.form.get('id', type=int))
        person.old_id = request.form.get('old_id', type=str)
        person.name = request.form.get('name', type=str)
        person.code = request.form.get('code', type=str)  
        db.session.flush()
        db.session.refresh(person)
        db.session.commit()
        return redirect(url_for('collectors'))
    else:
        person = Collectors.query.get(id_collector)
        return render_template('edit_collector.html', person=person)

@app.route('/collectors')
@login_required
def collectors_view():
    collectors = Collectors.query.order_by('code').all()
    return render_template('collectors.html', collectors=collectors)

@app.route("/add/keyword", methods=['POST','GET'])
@login_required
def add_keyword():
    if request.form:
        
        old_id = request.form.get('old_id', type=str)
        word = request.form.get('word', type=str)
        definition = request.form.get('definition', type=str)

        keyword = Keywords(old_id=old_id, word=word, definition=definition)
        
        db.session.add(keyword)
        db.commit()
        
        return redirect(url_for('keywords'))
    else:
        return render_template('add_keyword.html')

@app.route("/keywords")
def keyword_view():
    keywords = Keywords.query.order_by('word').all()
    return render_template('keywords.html', keywords=keywords)

@app.route("/add/informator", methods=['POST','GET'])
@login_required
def add_informator():
    if request.form:
        
        old_id = request.form.get('old_id', type=str)
        code = request.form.get('code', type=str)
        name = request.form.get('name', type=str)
        gender = request.form.get('gender', type=str)
        birth_year = request.form.get('birth_year', type=int)
        bio = request.form.get('bio', type=str)
        current_region = request.form.get('current_region', type=str)
        current_district = request.form.get('current_district', type=str)
        current_village = request.form.get('current_village', type=str)
        birth_region = request.form.get('birth_region', type=str)
        birth_district = request.form.get('birth_district', type=str)
        birth_village = request.form.get('birth_village', type=str)

        informator = Informators(
            old_id=old_id, code=code, name=name, gender=gender, birth_year=birth_year, bio=bio,
            current_region=current_region, current_district=current_district, current_village=current_village,
            birth_region=birth_region, birth_district=birth_district, birth_village=birth_village
            )
        
        db.session.add(informator)
        db.commit()
        
        return redirect(url_for('informators'))
    else:
        return render_template('add_informator.html')

@app.route('/informators')
@login_required
def informators_view():
    informators = Informators.query.order_by('name').all()
    return render_template('informators.html', informators=informators)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/results", methods=['GET'])
def results():
    if request.args and 'download' in request.args:
        return download_file(request)
    if request.args:
        result = get_result(request) 
        return render_template('results.html', result=result)
    return render_template('results.html', result=[])

def download_file(request):
    #response = Response("")
    #response = HttpResponse(text, content_type='text/txt; charset=utf-8')
    #response['Content-Disposition'] = 'attachment; filename="result.txt"'
    if request.args:
        text = ""
        result = get_result(request)
        for item in result[:MAX_RESULT]:
            text = text + 'ID:\t' + str(item.id) + '\n'
            text = text + 'Оригинальный ID:\t' + str(item.old_id) + '\n'
            text = text + 'Год:\t' + str(item.year) + '\n'
            text = text + 'Регион:\t' + str(item.region) + '\n'
            text = text + 'Район:\t' + str(item.district) + '\n'
            text = text + 'Населенный пункт:\t' + str(item.village) + '\n'
            text = text + 'Жанр:\t' + str(item.genre) + '\n'
            text = text + 'Информанты:\t' + ';'.join('{}, {}, {}'.format(i.code, i.birth_year, i.gender) for i in item.informators) + '\n'
            text = text + 'Вопросы:\t' + ';'.join('{}, {}'.format(i.question_list, i.question_code) for i in item.questions) + '\n'
            text = text + 'Ключевые слова:\t' + str(item.keywords) + '\n'
            text = text + '='*100 + '\n'
        response = Response(text, mimetype='text/txt')
    else:
        response = Response("", mimetype='text/txt')
    response.headers['Content-Disposition'] = 'attachment; filename={}.txt'.format(datetime.now())
    return response

@app.route('/user')
@login_required
def user():
    return render_template('user.html')

@app.route('/help_user')
@login_required
def help_user():
    return render_template('help_user.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stats')
def stats():
    result = {}
    stmt = select([
        func.count(Texts.id).label('N'),
        Texts.region,
        Texts.district,
        Texts.village
        ]).group_by("region, district, village").order_by("region, district, village")
    result['geostats'] = [GeoStats(i) for i in db.session.execute(stmt).fetchall()]
    print (result)
    return render_template('stats.html', result=result)


def get_result(request):
        result = Texts.query.filter()
        # year
        if request.args.get('year_from', type=int) is not None:
            result = result.filter(Texts.year >= request.args.get('year_from', type=int))
        if request.args.get('year_to', type=int) is not None:
            result = result.filter(Texts.year <= request.args.get('year_to', type=int))
        # id, old_id
        if request.args.get('id', type=int) is not None:
            result = result.filter(Texts.id==request.args.get('id', type=int))
        if request.args.get('old_id', type=str) not in ('', None):
            print (request.args.get('old_id', type=str))
            result = result.filter(Texts.old_id==request.args.get('old_id', type=str))
        # question list, code
        if request.args.getlist('question_list', type=str) != []:
            result = result.join(TQ, Questions).filter(Questions.question_list.in_(request.args.getlist('question_list', type=str)))
        if request.args.getlist('question_code', type=str) != []:
            result = result.join(TQ, Questions).filter(Questions.question_code.in_(request.args.getlist('question_code', type=str)))
        #text geo
        if request.args.getlist('region', type=str) != []:
            result = result.filter(Texts.region.in_(request.args.getlist('region', type=str)))
        if request.args.getlist('district', type=str) != []:
            result = result.filter(Texts.district.in_(request.args.getlist('district', type=str)))
        if request.args.getlist('village', type=str) != []:
            print (request.args.getlist('village', type=str))
            result = result.filter(Texts.village.in_(request.args.getlist('village', type=str)))
        #informator meta
        #result = result.join(TI, Informators)
        if request.args.getlist('code', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.code.in_(request.args.getlist('code', type=str))))
        if request.args.getlist('current_region', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.current_region.in_(request.args.getlist('current_region', type=str))))
        if request.args.getlist('current_district', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.current_district.in_(request.args.getlist('current_district', type=str))))
        if request.args.getlist('current_village', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.current_village.in_(request.args.getlist('current_village', type=str))))
        if request.args.getlist('birth_region', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.birth_region.in_(request.args.getlist('birth_region', type=str))))
        if request.args.getlist('birth_district', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.birth_district.in_(request.args.getlist('birth_district', type=str))))
        if request.args.getlist('birth_village', type=str) != []:
            result = result.filter(Texts.informators.any(Informators.birth_village.in_(request.args.getlist('birth_village', type=str))))

        result = [TextForTable(text) for text in result.all()]
        return result

def database_fields():
    selection = {}
    none = ('',' ','-',None)
    selection['question_list'] = [i for i in sorted(set(i.question_list for i in Questions.query.all() if i.question_list not in none))]
    selection['question_code'] = [i for i in sorted(set(i.question_code for i in Questions.query.all() if i.question_code not in none))]
    selection['region'] = [i for i in sorted(set(i.region for i in Texts.query.all() if i.region not in none))]
    selection['district'] = [i for i in sorted(set(i.district for i in Texts.query.all() if i.district not in none))]
    selection['village'] = [i for i in sorted(set(i.village for i in Texts.query.all() if i.village not in none))]
    selection['keywords'] = [i for i in sorted(set(i.word for i in Keywords.query.all() if i.word not in none))]

    selection['code'] = [i for i in sorted(set(i.code for i in Informators.query.all() if i.code is not none))]
    selection['current_region'] = [i for i in sorted(set(i.current_region for i in Informators.query.all() if i.current_region not in none))]
    selection['current_district'] = [i for i in sorted(set(i.current_district for i in Informators.query.all() if i.current_district not in none))]
    selection['current_village'] = [i for i in sorted(set(i.current_village for i in Informators.query.all() if i.current_village not in none))]
    selection['birth_region'] = [i for i in sorted(set(i.birth_region for i in Informators.query.all() if i.birth_region not in none))]
    selection['birth_district'] = [i for i in sorted(set(i.birth_district for i in Informators.query.all() if i.birth_district not in none))]
    selection['birth_village'] = [i for i in sorted(set(i.birth_village for i in Informators.query.all() if i.birth_village not in none))]
    return selection