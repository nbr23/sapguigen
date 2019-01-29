from app import app
from flask import render_template, request, Response
from sapgui.sapxmlparser import SAPXMLParser, XMLElement
from sapgui.saputils import SAPUtils

@app.route('/generate', methods=['POST'])
def generate():
    if 'sap_systems' not in request.form:
        return 'ERROR'
    parser = SAPXMLParser()
    slist = []
    instances = []
    root = parser.parse_logon_tree('<SAPTREE><Nodes><Favorites name="Favorites" expanded="1"/><Shortcuts name="Shortcuts" expanded="1"/><Connections name="Connections" expanded="1"/></Nodes></SAPTREE>', slist)
    parser.insert_nodes(root, 'Connections', request.form['sap_systems'])
    parser.get_instances(root, instances)
    response = Response(parser.get_SAPUILandscape(root, instances), status=200, mimetype='text/xml')
    response.headers['Content-Disposition'] = 'attachment; filename="SAPUILandscape.xml"'
    return response

@app.route('/')
def index():
    return render_template('sapguigen.html', title='SAPGui configuration generator')

