# coding:utf8
import os

__BASE_DIR__ = os.path.dirname(os.path.dirname(__file__))

configs = dict(
    debug=True,
    template_path=os.path.join(__BASE_DIR__, 'front', 'template'),
    static_path=os.path.join(__BASE_DIR__, 'front', 'template')
)
