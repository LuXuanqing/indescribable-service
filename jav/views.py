from flask import request, send_file, make_response, jsonify
from jav import app, db
from jav.models import Av, History
from jav import bots
from jav.log import create_logger

logger = create_logger(__name__)


@app.route('/content')
def content():
    res = make_response(send_file('templates/content.html'))
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


@app.route('/api/av/<id>', methods=['POST'])
def check_av(id, genres=None, casts=None):
    """
    更新genres, casts，并获取imgs, 上次访问

    :param id: av的番号，例如SSNI-413
    :param genres: 类别，默认不穿，自动从request中解析
    :param casts: 演员，默认不穿，自动从request中解析
    :return: {imgs}
    """
    av = fetch_av(id)
    last_visit = History.query.filter_by(av_id='av.id').order_by(History.timestamp.desc()).first()
    logger.debug(last_visit)

    # 如果本来没有genres, casts，则更新该字段
    data = request.get_json()
    is_changed = False
    if av.genres is None and data.get('genres'):
        av.genres = data['genres']
        is_changed = True
    if av.casts is None and data.get('casts'):
        av.casts = data['casts']
        is_changed = True
    # 如果更新了，则写入数据库
    if is_changed:
        av.to_str()
        db.session.commit()
        logger.info('Updated info of {}'.format(av))

    result = {
        'imgs': get_imgs_from_av(av),
        'lastVisit': {
            'timestamp': last_visit.timestamp if last_visit else None,
            'site': last_visit.site if last_visit else None
        }
    }
    # 记录这次访问
    # TODO 用装饰器做成每次请求后自动添加访问记录
    logger.debug('referrer: {}'.format(request.referrer))
    this_visit = History(av_id=av.id, site=request.referrer)
    db.session.add(this_visit)
    av.to_str()
    db.session.commit()
    logger.info('Insert {}'.format(this_visit))

    res = make_response(jsonify(result))
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res


def fetch_av(id):
    # 从数据库查询，没有则新建
    av = Av.query.get(id)
    if not av:
        av = Av(id=id)
        db.session.add(av)
        db.session.commit()
        logger.info('Inserted {}.'.format(av))
    return av


def get_imgs_from_av(av):
    # 如果没有图片，从网上爬
    if av.imgs is None:
        imgs = bots.get_previews(av.id)
        if imgs:
            av.imgs = imgs
            av.to_str()
            db.session.commit()
            logger.info('Updated imgs of {}'.format(av))
    return av.to_json().imgs


@app.route('/api/av/<id>/imgs', methods=['GET', 'POST'])
def handle_av_imgs(id):
    av = fetch_av(id)
    if request.method == 'GET':
        # TODO 如果返回数据为空，应该不是200
        return jsonify(get_imgs_from_av(av))

    if request.method == 'POST':
        # TODO 浏览javbus时自动post图片，省去再爬
        # 如果av没有imgs，并且post的data中有imgs，则写入数据库
        pass


@app.route('/api/av/<id>/dislike')
def av_dislike(id):
    # TODO implement this fn
    pass


@app.route('/api/av/<id>/need-hd')
def av_need_hd(id):
    # TODO implement this fn
    pass
