"""
    jqplot wrapper
"""

import re
import json
import uuid

from zoom import system

JQPLOT_SCRIPTS = [
    "/static/dz/jqplot/excanvas.js",
    "/static/dz/jqplot/jquery.jqplot.min.js",
    "/static/dz/jqplot/plugins/jqplot.highlighter.min.js",
    "/static/dz/jqplot/plugins/jqplot.cursor.min.js",
    "/static/dz/jqplot/plugins/jqplot.dateAxisRenderer.min.js",
    "/static/dz/jqplot/plugins/jqplot.canvasTextRenderer.min.js",
    "/static/dz/jqplot/plugins/jqplot.canvasAxisTickRenderer.min.js",
    "/static/dz/jqplot/plugins/jqplot.barRenderer.min.js",
    "/static/dz/jqplot/plugins/jqplot.categoryAxisRenderer.min.js",
    "/static/dz/jqplot/plugins/jqplot.pointLabels.min.js",
    "/static/dz/jqplot/plugins/jqplot.pieRenderer.min.js",
    "/static/dz/jqplot/plugins/jqplot.meterGaugeRenderer.min.js",
]

JQPLOT_STYLES = [
    "/static/dz/jqplot/jquery.jqplot.min.css"
]

JQPLOT_JS = """
        $(document).ready(function(){
            var data = %(data)s;
            var options = %(options)s;
            var plot1 = $.jqplot('%(chart_id)s', data, options);

            $( window ).resize(function() {
              // work around unpatched jqplot bug for bar width resize
              $.each(plot1.series, function(index, series) {
                series.barWidth = undefined;
              });
              plot1.replot( { resetAxes: true } );
            });
          });
"""

CHART_TPL = """
    <div id="%(chart_id)s" class="chart"></div>
"""

def merge_options(old, updates):
    """Merges two sets of options

    >>> from pprint import pprint
    >>> options1 = {
    ...     'setting_one': 10,
    ...     'setting_two': 20,
    ...     'setting_three': {
    ...         'setting_four': 'test',
    ...         'setting_five': [1, 2, 3],
    ...     },
    ...     'setting_six': 30,
    ... }
    >>> options2 = {
    ...     'setting_one': 30,
    ...     'setting_three': {
    ...         'setting_five': [1,2],
    ...     },
    ... }
    >>> pprint(merge_options(options1, options2))
    {'setting_one': 30,
     'setting_six': 30,
     'setting_three': {'setting_five': [1, 2], 'setting_four': 'test'},
     'setting_two': 20}

    >>> pprint(merge_options(options1, None))
    {'setting_one': 10,
     'setting_six': 30,
     'setting_three': {'setting_five': [1, 2, 3], 'setting_four': 'test'},
     'setting_two': 20}


    """
    if updates == None:
        return old

    elif hasattr(old, 'keys') and hasattr(updates, 'keys'):
        new = {}
        for k in old:
            new[k] = old[k]
        for k in updates:
            if k in new:
                new[k] = merge_options(new[k], updates[k])
            else:
                new[k] = updates[k]
        return new

    else:
        return updates




def render_options(default_options, options, k=None):
    """Merges options with default options and inserts plugins"""
    is_plugin = r'\"\$\.jqplot\.(.*)"'
    combined = merge_options(merge_options(default_options, options), k)
    result = json.dumps(combined, sort_keys=True, indent=4)
    return re.sub(is_plugin, lambda a: '$.jqplot.'+a.group(1), result)


def chart(parameters):
    """assemble chart components"""
    system.libs = system.libs | JQPLOT_SCRIPTS
    system.styles = system.styles | JQPLOT_STYLES
    system.js.add(JQPLOT_JS % parameters)
    return CHART_TPL % parameters


def line(data, legend=None, options=None, **k):
    """produce a line chart"""

    # pylint: disable=star-args
    # It's reasonable in this case.

    chart_id = k.pop('chart_id', 'chart_' + uuid.uuid4().hex)

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

    if len(data) > 1:
        labels, data = data[0], data[1:]
        default_options['axes']['xaxis']['ticks'] = labels

    if legend:
        default_options['legend'] = dict(show='true', placement='insideGrid')
        default_options['series'] = [dict(label=label) for label in legend]

    parameters = dict(
        chart_id=chart_id,
        data=json.dumps(data),
        options=render_options(default_options, options, k),
        )

    return chart(parameters)


def bar(data, legend=None, options=None, **k):
    """produce a bar chart"""
    # pylint: disable=blacklisted-name
    # It's reasonable in this case.

    # pylint: disable=star-args
    # It's reasonable in this case.

    chart_id = k.pop('chart_id', 'chart_' + uuid.uuid4().hex)

    data = zip(*data)

    default_options = {
        'seriesDefaults': {
            'renderer': '$.jqplot.BarRenderer',
            'rendererOptions': {'fillToZero': True, 'useNegativeColors': False}
            },
        }

    if len(data) > 1:
        labels, data = data[0], data[1:]
        default_options.setdefault('axes', {})
        default_options['axes'].setdefault('xaxis', {})
        default_options['axes']['xaxis'].setdefault('renderer',
                                            '$.jqplot.CategoryAxisRenderer')
        default_options['axes']['xaxis'].setdefault('ticks', labels)

    if legend:
        default_options['legend'] = dict(show='true', placement='outsideGrid')
        default_options['series'] = [dict(label=label) for label in legend]

    parameters = dict(
        chart_id=chart_id,
        data=json.dumps(data),
        options=render_options(default_options, options, k),
    )

    return chart(parameters)


def hbar(data, legend=None, options=None, **k):
    """produce a horizontal bar chart"""

    # pylint: disable=star-args
    # It's reasonable in this case.

    chart_id = k.pop('chart_id', 'chart_' + uuid.uuid4().hex)

    data = zip(*data)

    default_options = {
        'seriesDefaults': {
            'renderer': '$.jqplot.BarRenderer',
            'rendererOptions': {
                'barDirection': 'horizontal',
                }
            },
        }

    if len(data) > 1:
        labels, data = data[0], data[1:]
        default_options.setdefault('axes', {})
        default_options['axes'].setdefault('yaxis', {})
        default_options['axes']['yaxis'].setdefault('renderer',
                                            '$.jqplot.CategoryAxisRenderer')
        default_options['axes']['yaxis'].setdefault('ticks', labels)

    if legend:
        default_options['legend'] = dict(show='true', placement='outsideGrid')
        default_options['series'] = [dict(label=label) for label in legend]

    parameters = dict(
        chart_id=chart_id,
        data=json.dumps(data),
        options=render_options(default_options, options, k),
    )

    return chart(parameters)


def pie(data, legend=None, options=None, **k):
    """produce a pie chart"""

    chart_id = k.pop('chart_id', 'chart_' + uuid.uuid4().hex)

    data = [[row[:2] for row in data]] # can only handle one series right now

    default_options = {
        'seriesDefaults': {
            'renderer': '$.jqplot.PieRenderer',
            'rendererOptions': {
                'showDataLabels': True,
                'sliceMargin': 5,
                'shadow': False,
                }
            },
        }

    if legend:
        default_options['legend'] = dict(show='true', location='e')

    parameters = dict(
        chart_id=chart_id,
        data=json.dumps(data),
        options=render_options(default_options, options, k),
    )

    return chart(parameters)


def gauge(data,
          label=None,
          intervals=None,
          interval_colors=None,
          options=None,
          **k):
    """produce a gauge chart"""

    chart_id = k.pop('chart_id', 'chart_' + uuid.uuid4().hex)

    data = [[data]]

    default_options = {
        'seriesDefaults': {
            'renderer': '$.jqplot.MeterGaugeRenderer',
            'rendererOptions': {
                'min': 0,
                'max': 5,
                }
            },
        }

    renderer_options = default_options['seriesDefaults']['rendererOptions']
    if label:
        renderer_options['label'] = label

    if intervals:
        renderer_options['intervals'] = intervals
        renderer_options['labelPosition'] = 'bottom'

    if interval_colors:
        renderer_options['intervalColors'] = interval_colors

    parameters = dict(
        chart_id=chart_id,
        data=json.dumps(data),
        options=render_options(default_options, options, k),
    )

    return chart(parameters)


def time_series(data, legend=None, time_format='%b %e', options=None, **k):
    """produce a time series chart"""

    chart_id = k.pop('chart_id', 'chart_' + uuid.uuid4().hex)

    fmt = '%m/%d/%Y %H:%M:%S'
    min_date = min(r[0] for r in data).strftime(fmt)
    max_date = max(r[0] for r in data).strftime(fmt)
    data = [
        [[r[0].strftime(fmt)]+list(r[n+1:n+2]) for r in data]
        for n in range(len(data[0])-1)
    ]

    default_options = {
            'highlighter': {
                'show': True,
                'sizeAdjust': 2.5,
                'tooltipSeparator': ' - ',
                'tooltipAxes': 'y',
                },
            'axes': {
                'xaxis': {
                    'renderer': '$.jqplot.DateAxisRenderer',
                    'tickOptions': {'formatString': time_format},
                    'min': min_date,
                    'max': max_date,
                    }
                }
            }

    if legend:
        default_options['legend'] = dict(show='true', placement='insideGrid')
        default_options['series'] = [dict(label=label) for label in legend]

    parameters = dict(
        chart_id=chart_id,
        data=json.dumps(data),
        options=render_options(default_options, options, k),
        )

    return chart(parameters)

