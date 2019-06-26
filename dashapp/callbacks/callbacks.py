from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_table
from flask_login import current_user
import pandas as pd
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
from collections import OrderedDict
from sqlalchemy.exc import IntegrityError
import csv
import dashapp.layout


def register_callbacks(app):
    from app import db
    from app.models import Transaction

    def update_changed_data(old_data, data):
        old = pd.DataFrame.from_records(old_data)
        new = pd.DataFrame.from_records(data)

        ne_stacked = (old != new).stack()

        changed = new.stack()[ne_stacked]
        idx = changed.index.get_level_values(0)[0]
        column = changed.index.get_level_values(1)[0]
        id = old.loc[idx, "id"]
        value = changed[0]

        try:
            transaction = Transaction.query.get(id)
            setattr(transaction, column, value)
            db.session.flush()
        except IntegrityError as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()

    def gen_conditionals_from_csv(src, category_column, sub_category_column):
        categories = {}
        with open(src) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                categories[row[0]] = [c for c in row[1:] if c != ""]

        conditional_dict = {
            category_column: {
                "options": [{"label": i, "value": i} for i in categories.keys()]
            }
        }

        sub_conditional_list = [
            {
                "if": {
                    "column_id": sub_category_column,
                    "filter_query": f'{{{category_column}}} eq "{category}"',
                },
                "options": [{"label": i, "value": i} for i in categories[category]],
            }
            for category in categories.keys()
        ]

        return conditional_dict, sub_conditional_list

    conditional_dict, sub_conditional_list = gen_conditionals_from_csv(
        "dashapp\\static\\categories.csv", "category", "sub_category"
    )

    @app.callback(
        Output("main", "children"),
        [Input("transaction_table", "data_previous")],
        [
            State("transaction_table", "data"),
            State("transaction_table", "page_current"),
        ],
    )
    def update_database_and_generate_table(old_table_data, table_data, page_current):
        with app.server.app_context():
            if old_table_data is not None:
                update_changed_data(old_table_data, table_data)
            transactions = db.session.query(Transaction)
            df = pd.read_sql(transactions.statement, transactions.session.bind)

        return [
            dash_table.DataTable(
                id="transaction_table",
                data=df.to_dict("rows"),
                columns=[
                    {"id": "id", "name": "Hash", "type": "text", "hidden": True},
                    {"id": "date", "name": "Date", "type": "text"},
                    {"id": "narration", "name": "Narration", "type": "text"},
                    {
                        "id": "debit",
                        "name": "Debit",
                        "type": "numeric",
                        "format": FormatTemplate.money(2),
                    },
                    {
                        "id": "credit",
                        "name": "Credit",
                        "type": "numeric",
                        "format": FormatTemplate.money(2),
                    },
                    {
                        "id": "category",
                        "name": "Category",
                        # "type": "text",
                        "presentation": "dropdown",
                    },
                    {
                        "id": "sub_category",
                        "name": "Sub-category",
                        # "type": "text",
                        "presentation": "dropdown",
                    },
                ],
                style_cell={"padding": "5px"},
                style_header={"backgroundColor": "white", "fontWeight": "bold"},
                editable=True,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                page_action="native",
                page_current=page_current,
                page_size=20,
                dropdown=conditional_dict,
                dropdown_conditional=sub_conditional_list,
            )
        ]

