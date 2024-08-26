from django.shortcuts import render, get_object_or_404
from .forms import ColumnSelectionForm
from data_reader.models import UploadedFile, FileColumn
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.http import JsonResponse
import json

config = {'displayModeBar': True}
config2 = {'displaylogo': False}

def plot_cmd(request):
    if request.method == 'POST':
        form = ColumnSelectionForm(request.POST, uploaded_files=UploadedFile.objects.all())

        if 'load_columns' in request.POST:
            if form.is_valid():
                uploaded_file_id = form.cleaned_data['uploaded_file'].id
                form.fields['x_column'].choices = form.get_column_choices(uploaded_file_id)
                form.fields['y_column'].choices = form.get_column_choices(uploaded_file_id)
                if form.cleaned_data.get('use_color_column', False):
                    form.fields['color_column'].choices = form.get_column_choices(uploaded_file_id)
                return render(request, 'cmd_plotter/cmd_plot.html', {'form': form})

        elif 'generate_plot' in request.POST:
            if form.is_valid():
                uploaded_file_id = form.cleaned_data['uploaded_file'].id
                x_column = form.cleaned_data['x_column']
                y_column = form.cleaned_data['y_column']
                use_color_column = form.cleaned_data.get('use_color_column', False)
                color_column = form.cleaned_data['color_column'] if use_color_column else None
                colorscale_choice = form.cleaned_data['colorscale_choice']
                invert_x_axis = form.cleaned_data.get('invert_x_axis', False)
                invert_y_axis = form.cleaned_data.get('invert_y_axis', False)
                log_x_axis = form.cleaned_data.get('log_x_axis', False)
                log_y_axis = form.cleaned_data.get('log_y_axis', False)

                try:
                    uploaded_file = get_object_or_404(UploadedFile, pk=uploaded_file_id)
                    file_path = uploaded_file.file.path
                    data_table = pd.read_csv(file_path)

                    selected_columns = [x_column, y_column]
                    if color_column:
                        selected_columns.append(color_column)

                    if not all(column in data_table.columns for column in selected_columns):
                        error_msg = 'Selected columns do not exist in the table. Available columns: ' + ', '.join(data_table.columns)
                        return render(request, 'cmd_plotter/error.html', {'error': error_msg})

                    fig  = go.Figure()

                    # Scatter plot
                    fig.add_trace(go.Scatter(
                        x=data_table[x_column],
                        y=data_table[y_column],
                        mode='markers',
                        marker=dict(
                            size=5,
                            color=data_table[color_column] if color_column else 'blue',
                            colorscale=colorscale_choice if color_column else None,
                            colorbar=dict(title=color_column) if color_column else None,
                            showscale=bool(color_column),
                            reversescale=True,
                        ),
                        hovertemplate=f'{x_column}: %{{x}}<br>{y_column}: %{{y}}<extra></extra>',
                        name='CMD'
                    ))

                    # Update layout
                    fig.update_layout(
                        height=800,
                        showlegend=False,
                        plot_bgcolor='white',
                        xaxis_title=f'{x_column}',
                        yaxis_title=f'{y_column}',
                        
                    )
                    fig.update_xaxes(mirror=True,
                                    ticks='outside',
                                    showline=True,
                                    linecolor='black',
                                    gridcolor='lightgrey'
                                    )
                    fig.update_yaxes(mirror=True,
                                    ticks='outside',
                                    showline=True,
                                    linecolor='black',
                                    gridcolor='lightgrey'
                                    )

                    plot_div = fig.to_html(full_html=False)
                    data_table_json = data_table.to_json(orient='split')

                    return render(request, 'cmd_plotter/cmd_plot.html', {
                        'form': form,
                        'plot_div': plot_div,
                        'config': config,
                        'config2': config2,
                        'data': data_table_json  # Pass the data as JSON to the template
                    })
                except Exception as e:
                    import traceback
                    error_msg = f"Error processing the file: {e}\n{traceback.format_exc()}"
                    return render(request, 'cmd_plotter/error.html', {'error': error_msg})

    else:
        form = ColumnSelectionForm(uploaded_files=UploadedFile.objects.all())

    return render(request, 'cmd_plotter/cmd_plot.html', {'form': form})

def process_selected_data(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            selected_data = json.loads(request.body)

            # Convert to DataFrame for processing
            df = pd.DataFrame(selected_data)

            # Print or process the DataFrame as needed
            print("Received selected data:", df)

            return JsonResponse({'message': 'Selected data received successfully'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)