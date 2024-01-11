from .app import app, login_required, PREFIX
from data_base import get_tiggers, get_all_chat, add_tiggers, get_tigger, update_tigger, delete_tigger
from flask import Flask, request, render_template, redirect, url_for, send_from_directory


@app.route(f'{PREFIX}/menu')
@login_required
def start():
    chats = get_tiggers()
    chart_labels = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
    chart_data = [12, 19, 3, 5, 2, 3]

    return render_template('menu.html', chats=chats, bot_user="Менеджер",  PREFIX=PREFIX, chart_labels=chart_labels, chart_data=chart_data)
