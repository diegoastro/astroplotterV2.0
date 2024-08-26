# imf_plotter/views.py
from django.shortcuts import render
from django.http import HttpResponse
import csv
from .forms import IMFPlotForm
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import scipy.optimize as sc
import plotly.offline as pyo

pyo.init_notebook_mode(connected=True)

def powerlaw(x, c, alpha):
    return c * x ** (-alpha)

def lognormal(x, c, logmc, sigma):
    return c * np.e ** (-(np.log10(x) - logmc) ** 2 / (2 * sigma ** 2))

def lognormal_and_powerlaw(x, c, logmc, sigma, alpha):
    return np.piecewise(x, [x < 1, x >= 1], [
        lambda x: c * np.e ** (-(np.log10(x) - logmc) ** 2 / (2 * sigma ** 2)), 
        lambda x: (c * np.e ** (-(logmc ** 2) / (2 * sigma ** 2))) * x ** (-alpha)
    ])

def imf_plot(request):
    if request.method == 'POST':
        try:
            form = IMFPlotForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = form.cleaned_data['uploaded_file'].file
                mass_column = form.cleaned_data['mass_column']
                log_scale = form.cleaned_data.get('log_scale', False)
                df = pd.read_csv(uploaded_file)

                if not log_scale:
                    df[mass_column] = np.log10(df[mass_column])
                    print(df[mass_column])  

                bins = np.arange(-3, 2, 0.1)
                hist_data = np.histogram(df[mass_column], bins=bins)
                mass_function_data = [hist_data[0], 0.5 * (hist_data[1][1:] + hist_data[1][:-1])]

                xdata = mass_function_data[1]
                ydata = mass_function_data[0]
                mask = xdata > 0

                salpeter = sc.curve_fit(powerlaw, 10 ** xdata[mask], ydata[mask])
                lognorm = sc.curve_fit(lognormal, 10 ** xdata, ydata)
                chabrier = sc.curve_fit(lognormal_and_powerlaw, 10 ** xdata, ydata)

                dt_fit = {
                    'Data': mass_function_data,
                    'Salpeter': salpeter,
                    'Lognormal': lognorm,
                    'Chabrier': chabrier,
                }

                buttons = []
                annotations = []
                i = 0

                default_option = {'label': 'Select parametrization', 'method': 'update', 'args': [{'visible': [True] + [False] * (len(dt_fit) - 1)}, {'annotations': [dict(x=0.5, y=1.05, xref='paper', yref='paper', text='', bgcolor='white', showarrow=False, font=dict(size=12))]}]}
                buttons.append(default_option)

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=xdata,
                    y=ydata,
                    mode='markers',
                    name='Data',
                    marker=dict(size=8, color=xdata, colorscale='Rainbow', symbol='hexagram', showscale=False, reversescale=True),
                    error_y=dict(type='data', array=np.sqrt(ydata), visible=True)
                ))

                for name, fits in dt_fit.items():
                    if name == 'Data':
                        continue

                    if name == 'Salpeter':
                        fit_y = powerlaw(10**xdata, *fits[0])
                        label = f'{name}:$$c={fits[0][0]:.2e},~~\\alpha={fits[0][1]:.2f}$$'
                    elif name == 'Lognormal':
                        fit_y = lognormal(10 ** xdata, *fits[0])
                        label = f'{name}:$$c={fits[0][0]:.2e},~~\\log(mc)={fits[0][1]:.2f},~~\\sigma={fits[0][2]:.2f}$$'
                    elif name == 'Chabrier':
                        fit_y = lognormal_and_powerlaw(10 ** xdata, *fits[0])
                        label = f'{name}:$$c={fits[0][0]:.2e},~~\\log(mc)={fits[0][1]:.2f},~~\\sigma={fits[0][2]:.2f},~~\\alpha={fits[0][3]:.2f}$$'

                    fig.add_trace(go.Scatter(
                        x=xdata,
                        y=fit_y,
                        mode='lines',
                        line_color='black',
                        name=name,
                        visible=False
                    ))

                    visibility_list = [True] + [False] * (len(dt_fit) - 1)
                    visibility_list[i+1] = True
                    buttons.append(dict(
                        label=name,
                        method='update',
                        args=[{'visible': visibility_list},
                              {'annotations': [dict(x=0.56, y=1.055, xref='paper', yref='paper', text=label, bgcolor = 'white',showarrow=False, font=dict(size=16))]}
                              ]
                    ))
                    i += 1

                fig.data[0].visible = True
                fig.update_xaxes(mirror=True,
                                ticks='outside',
                                showline=True,
                                linecolor='black',
                                gridcolor='lightgrey'
                                )
                fig.update_yaxes(type='log',
                                 mirror=True,
                                ticks='outside',
                                showline=True,
                                linecolor='black',
                                gridcolor='lightgrey'
                                 )
                fig.update_layout(plot_bgcolor='white',
                    updatemenus=[
                        dict(
                            type='dropdown',
                            direction='down',
                            x=0.99,
                            y=0.99,
                            xanchor = 'right',
                            yanchor = 'top',
                            buttons=buttons
                        )
                    ],
                    title={
                        'text':f'IMF parameters:',
                        'y':0.89,
                        'x':0.1,
                        'xanchor':'left',
                        'yanchor':'top',
                            },
                    xaxis_title='$$\\log(M/M_{\\odot})$$',
                    yaxis_title='$$\\log(N)$$',
                    height=700,
                    width=900,
                    legend=dict(
                        x=1.05,
                        y=1,
                        traceorder='normal',
                        font=dict(
                            family='sans-serif',
                            size=12,
                            color='black'
                        ),
                    ),
                )

                plot_div = fig.to_html(full_html=False)

                # Save the data to session for later use
                request.session['plot_data'] = {
                    'xdata': xdata.tolist(),
                    'ydata': ydata.tolist(),
                    'parameters': {
                        'Salpeter': salpeter[0].tolist(),
                        'Lognormal': lognorm[0].tolist(),
                        'Chabrier': chabrier[0].tolist(),
                    }
                }

                context = {'form': form, 'plot_div': plot_div}
                return render(request, 'imf_plotter/imf_plot.html', context)
        
        except Exception as e:
            import traceback
            error_msg = f"Error processing the file: {e}\n{traceback.format_exc()}"
            return render(request, 'imf_plotter/error.html', {'error': error_msg})
    else:
        form = IMFPlotForm()

    return render(request, 'imf_plotter/imf_plot.html', {'form': form})

def data_download(request):
    plot_data = request.session.get('plot_data', None)
    if not plot_data:
        return HttpResponse('No data available for download.', status=400)

    xdata = plot_data['xdata']
    ydata = plot_data['ydata']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="param_and_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Parametrization', 'c', 'alpha', 'sigma', 'logmc'])
    writer.writerow(['Salpeter'] + plot_data['parameters']['Salpeter'])
    writer.writerow(['Lognormal'] + plot_data['parameters']['Lognormal'])
    writer.writerow(['Chabrier'] + plot_data['parameters']['Chabrier'])
   
    writer.writerow(['m/m_sun', 'n'])
    writer.writerows(zip(xdata, ydata))
    
    return response
