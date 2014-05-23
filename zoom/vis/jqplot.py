
import re
import json
import uuid


css = """
    .chart {
        height:300px; 
        width:600px;
        margin: 30px 0;
    }
    .jqplot-axis {
        font-size: 0.8em;
    }
    .jqplot-xaxis {
        padding-top: 10px;
    }
    .jqplot-yaxis {
        padding-right: 10px;
    }
"""
css = css


head = """
    <link rel="stylesheet" type="text/css" href="/static/jqplot/jquery.jqplot.min.css" />
    <script type="text/javascript" src="/static/excanvas.js"></script>
    <script type="text/javascript" src="/static/jqplot/jquery.jqplot.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.highlighter.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.cursor.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.dateAxisRenderer.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.canvasTextRenderer.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.canvasAxisTickRenderer.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.barRenderer.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.categoryAxisRenderer.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.pointLabels.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.pieRenderer.min.js"></script>
    <script type="text/javascript" src="/static/jqplot/plugins/jqplot.meterGaugeRenderer.min.js"></script>
"""

chart_tpl = """
    <div id="chart_%(name)s" class="chart"></div>
    <script class="code" type="text/javascript">
        $(document).ready(function(){
            var data = %(data)s;
            var options = %(options)s;
            var plot1 = $.jqplot('chart_%(name)s', data, options);
          });
    </script>
"""

def merge_options(a, b):
    """Merges two sets of options"""
    if hasattr(a,'keys') and hasattr(b,'keys'):
        c = {}
        for k in a:
            c[k] = a[k]
        for k in b:
            if k in c:
                c[k] = merge_options(c[k],b[k])
            else:
                c[k] = b[k]
        return c
    else:
        return b

PLUGIN = '\"\$\.jqplot\.(.*)"' 

def render_options(default_options, options, k={}):
    """Merges options with default options and inserts plugins"""
    combined = merge_options(merge_options(default_options, options), k)
    result = json.dumps(combined, sort_keys=True, indent=4)
    return re.sub(PLUGIN, lambda a: '$.jqplot.'+a.group(1), result)


def line(data, legend=None, options={}, *a, **k):

    chart_name = uuid.uuid4().hex

    data = zip(*data)

    default_options = {
            'highlighter': {
                'show': True,
                'sizeAdjust': 7.5,
                'tooltipSeparator': ' - ',
                'tooltipAxes': 'y',
                },
            'axes': {
                'xaxis': {
                    'renderer': '$.jqplot.CategoryAxisRenderer',
                    }
                }
            }

    if len(data)>1:  
        labels, data = data[0], data[1:]
        default_options['axes']['xaxis']['ticks'] = labels

    if legend:
        default_options['legend'] = dict(show='true', placement='insideGrid')
        default_options['series'] = [dict(label=label) for label in legend]

    v = dict(
        name = chart_name,
        data = json.dumps(data),
        options = render_options(default_options, options, k),
        )

    return chart_tpl % v

def hbar(data, legend=None, options={}, *a, **k):

    chart_name = uuid.uuid4().hex

    data = zip(*data)

    default_options = {
        'seriesDefaults': {
            'renderer': '$.jqplot.BarRenderer',
            'rendererOptions': {
                'barDirection': 'horizontal',
                }
            },
        }

    if len(data)>1:  
        labels, data = data[0], data[1:]
        options['axes'] = dict(
                yaxis=dict(
                    renderer='$.jqplot.CategoryAxisRenderer',
                    ticks=labels,
                    )
                )

    if legend:
        options['legend'] = dict(show='true', placement='outsideGrid')
        options['series'] = [dict(label=label) for label in legend]

    v = dict (
        name = chart_name,
        data = json.dumps(data),
        options = render_options(default_options, options, k),
    )

    return chart_tpl % v

