# virtual environment ka name venv h
from datetime import date, datetime ,date as dt_date
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for, make_response, flash, redirect,Response, jsonify
from sqlalchemy import func
import csv
import io
import os
import json
import secrets
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file in the project root, if present

app= Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

# SECRET_KEY should stay stable across restarts (it signs sessions/flash messages).
# Set it in .env; if it's missing we fall back to a random one so the app still
# runs, but you'll lose flash messages/sessions on every restart until you set it.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
db=SQLAlchemy(app)

# AI chatbot client - reads the key from .env / the environment, never hardcode it here
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
ai_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
AI_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


class Expense(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False,default=date.today)

with app.app_context():
    db.create_all()


CATEGORIES =["🍔 Food",
"🚌 Transport",
"🏠 Rent",
"💡 Utilities",
"🏥 Health",
"🛒 Shopping",
"🎬 Entertainment",
"🎓 Education",
"✈️ Travel",
"🧾 Bills",
"🥬 Groceries",
"⛽ Fuel",
"🌐 Internet",
"📱 Mobile Recharge",
"🛡️ Insurance",
"💳 EMI",
"📺 Subscriptions",
"💻 Technology",
"💄 Personal Care",
"🎁 Gifts",
"👨‍👩‍👧 Family",
"🐶 Pets",
"💪 Fitness",
"📈 Investments",
"❤️ Charity",
"🔧 Maintenance",
"🏛️ Taxes",
"💼 Office",
"📦 Miscellaneous",
"❓ Other"]



def parse_date_or_none(s: str):
    if not s:
        return None
    try:
        return datetime.strptime(s,"%Y-%m-%d").date()
    except ValueError:
        return None

@app.route("/")
def index():
    # read query strings
    start_str=(request.args.get("start") or "").strip()
    end_str = (request.args.get("end") or "").strip()
    selected_category=(request.args.get("category") or "").strip()

    #  parsing
    start_date=parse_date_or_none(start_str)
    end_date = parse_date_or_none(end_str)

    if start_date and end_date and end_date < start_date:
        flash("End date cannot be before start date","error")
        start_date = end_date= None
        start_str= end_str = ""





    q=Expense.query
    if start_date:
        q=q.filter(Expense.date>=start_date)
    if end_date:
        q=q.filter(Expense.date <= end_date)

    if selected_category:
        q = q.filter(Expense.category == selected_category)





    expenses= q.order_by(Expense.date.desc(),
                                     Expense.id.desc()).all()
    total=round(sum(e.amount for e in expenses),2)

    # print(expenses)
    # #this is for piechart
    cat_q= db.session.query(Expense.category,func.sum(Expense.amount))
    if start_date:
        cat_q=cat_q.filter(Expense.date >= start_date)

    if end_date:
        cat_q = cat_q.filter(Expense.date <= end_date)
    if selected_category:
        cat_q= cat_q.filter(Expense.category == selected_category)

    cat_rows = cat_q.group_by(Expense.category).all()
    cat_labels = [ c for c, _ in cat_rows]
    cat_values = [round(float(s or 0),2) for _, s in cat_rows]

    # day chart --> bar graph
    day_q = db.session.query(Expense.date, func.sum(Expense.amount))
    if start_date:
        day_q = day_q.filter(Expense.date >= start_date)

    if end_date:
        day_q = day_q.filter(Expense.date <= end_date)
    if selected_category:
        day_q = day_q.filter(Expense.category == selected_category)
    #
    day_rows = day_q.group_by(Expense.category).order_by(Expense.date).all()
    day_labels = [d.isoformat() for d, _ in day_rows]
    day_values = [round(float(s or 0), 2) for _, s in day_rows]



    return render_template(
        "index.html",
        selected_category=selected_category,
        expenses=expenses,
        today=date.today().isoformat(),
        categories=CATEGORIES,
        total=total,
        start_str=start_str,
        end_str=end_str,
        cat_labels=cat_labels,
        cat_values=cat_values,
    day_labels = day_labels,
    day_values = day_values


    )

@app.route("/add",methods=['POST'])
def add():

    description= (request.form.get("description") or "").strip()
    amount_str = (request.form.get("amount") or "").strip()
    category = (request.form.get("category") or "").strip()
    date_str = (request.form.get("date") or "").strip()

    if not description or not amount_str or not category:
        flash("Please fill all fields","error")
        return redirect(url_for("index"))


    try:
        amount=float(amount_str)
        if amount<=0:
            raise ValueError
    except ValueError:
            flash("amount must be a positive number","error")
            return redirect(url_for("index"))

    try:
        d=datetime.strptime(date_str,"%Y-%m-%d").date() if date_str else date.today()
    except ValueError:
        d= date.today()
    e=Expense(description=description,amount=amount,category=category,date=d)
    db.session.add(e)
    db.session.commit()

    flash("Expense added","success")
    return redirect(url_for("index"))

@app.route('/delete/<int:expense_id>',methods=['POST'])
def delete(expense_id):
    e=Expense.query.get_or_404(expense_id)
    db.session.delete(e)
    db.session.commit()
    flash("Expense deleted","success")
    return redirect(url_for("index"))



@app.route("/export.csv")
def export_csv():

    start_str = (request.args.get("start") or "").strip()
    end_str = (request.args.get("end") or "").strip()
    selected_category = (request.args.get("category") or "").strip()

    start_date = parse_date_or_none(start_str)
    end_date = parse_date_or_none(end_str)

    q = Expense.query

    if start_date:
        q = q.filter(Expense.date >= start_date)

    if end_date:
        q = q.filter(Expense.date <= end_date)

    if selected_category:
        q = q.filter(Expense.category == selected_category)

    expenses = q.order_by(Expense.date, Expense.id).all()

    lines = [
        f"Start Date,{start_str or 'All'}",
        f"End Date,{end_str or 'All'}",
        f"Category,{selected_category or 'All'}",
        f"Exported On,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "date,description,category,amount"
    ]

    for e in expenses:
        lines.append(
            f"{e.date.isoformat()},{e.description},{e.category},{e.amount:.2f}"
        )

    csv_data = "\n".join(lines)

    fname_start = start_str or "all"
    fname_end = end_str or "all"

    filename = f"expenses_{fname_start}_to_{fname_end}.csv"

    return Response(
        "\ufeff" + csv_data,  # Add UTF-8 BOM
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

@app.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
def edit(expense_id):

    e = Expense.query.get_or_404(expense_id)

    if request.method == "POST":

        e.description = (request.form.get("description") or "").strip()
        e.amount = float(request.form.get("amount"))
        e.category = (request.form.get("category") or "").strip()

        date_str = (request.form.get("date") or "").strip()

        try:
            e.date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            e.date = dt_date.today()

        db.session.commit()

        flash("Expense updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template(
        "edit.html",
        expense=e,
        categories=CATEGORIES,
        today=dt_date.today().isoformat()
    )



# ---------------------------------------------------------------------------
# AI chatbot: tool definitions (OpenAI/Groq function-calling format)
# ---------------------------------------------------------------------------

AI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Add a new expense record to the tracker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Short description of the expense"},
                    "amount": {"type": "number", "description": "Positive amount spent"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format. Omit to use today."},
                },
                "required": ["description", "amount", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_expense",
            "description": "Update one or more fields of an existing expense, identified by its id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expense_id": {"type": "integer"},
                    "description": {"type": "string"},
                    "amount": {"type": "number"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                },
                "required": ["expense_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_expense",
            "description": "Delete an expense by its id.",
            "parameters": {
                "type": "object",
                "properties": {"expense_id": {"type": "integer"}},
                "required": ["expense_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_expenses",
            "description": "List individual expenses, optionally filtered by date range and/or category. Use this to find the id of an expense the user is referring to, or to inspect recent activity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "category": {"type": "string", "enum": CATEGORIES},
                    "limit": {"type": "integer", "description": "Max rows to return, default 50"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get the total spend and a breakdown by category for a date range and/or category. Use this for any question about totals, averages, or trends instead of guessing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "category": {"type": "string", "enum": CATEGORIES},
                },
            },
        },
    },
]


def _expense_to_dict(e):
    return {
        "id": e.id,
        "description": e.description,
        "amount": e.amount,
        "category": e.category,
        "date": e.date.isoformat() if e.date else None,
    }


def run_ai_tool(name, tool_input):
    """Executes a single tool call requested by the model and returns a JSON-able result."""
    try:
        if name == "add_expense":
            description = (tool_input.get("description") or "").strip()
            category = (tool_input.get("category") or "").strip()
            amount = float(tool_input.get("amount"))

            if not description:
                return {"error": "description is required"}
            if category not in CATEGORIES:
                return {"error": f"'{category}' is not a valid category", "valid_categories": CATEGORIES}
            if amount <= 0:
                return {"error": "amount must be a positive number"}

            d = parse_date_or_none(tool_input.get("date")) or date.today()
            e = Expense(description=description, amount=amount, category=category, date=d)
            db.session.add(e)
            db.session.commit()
            return {"success": True, "expense": _expense_to_dict(e)}

        elif name == "update_expense":
            e = Expense.query.get(tool_input.get("expense_id"))
            if not e:
                return {"error": "No expense found with that id"}

            if tool_input.get("description"):
                e.description = tool_input["description"].strip()
            if tool_input.get("amount") is not None:
                amount = float(tool_input["amount"])
                if amount <= 0:
                    return {"error": "amount must be a positive number"}
                e.amount = amount
            if tool_input.get("category"):
                if tool_input["category"] not in CATEGORIES:
                    return {"error": f"'{tool_input['category']}' is not a valid category", "valid_categories": CATEGORIES}
                e.category = tool_input["category"]
            if tool_input.get("date"):
                d = parse_date_or_none(tool_input["date"])
                if not d:
                    return {"error": "date must be in YYYY-MM-DD format"}
                e.date = d

            db.session.commit()
            return {"success": True, "expense": _expense_to_dict(e)}

        elif name == "delete_expense":
            e = Expense.query.get(tool_input.get("expense_id"))
            if not e:
                return {"error": "No expense found with that id"}
            db.session.delete(e)
            db.session.commit()
            return {"success": True}

        elif name == "list_expenses":
            q = Expense.query
            start_date = parse_date_or_none(tool_input.get("start_date"))
            end_date = parse_date_or_none(tool_input.get("end_date"))
            category = tool_input.get("category")
            limit = tool_input.get("limit") or 50

            if start_date:
                q = q.filter(Expense.date >= start_date)
            if end_date:
                q = q.filter(Expense.date <= end_date)
            if category:
                q = q.filter(Expense.category == category)

            rows = q.order_by(Expense.date.desc(), Expense.id.desc()).limit(limit).all()
            return {"expenses": [_expense_to_dict(r) for r in rows]}

        elif name == "get_summary":
            q = Expense.query
            start_date = parse_date_or_none(tool_input.get("start_date"))
            end_date = parse_date_or_none(tool_input.get("end_date"))
            category = tool_input.get("category")

            if start_date:
                q = q.filter(Expense.date >= start_date)
            if end_date:
                q = q.filter(Expense.date <= end_date)
            if category:
                q = q.filter(Expense.category == category)

            rows = q.all()
            total = round(sum(r.amount for r in rows), 2)
            by_category = {}
            for r in rows:
                by_category[r.category] = round(by_category.get(r.category, 0) + r.amount, 2)

            return {"total": total, "count": len(rows), "by_category": by_category}

        else:
            return {"error": f"Unknown tool '{name}'"}

    except Exception as ex:
        return {"error": str(ex)}


@app.route("/api/chat", methods=["POST"])
def chat():
    if ai_client is None:
        return jsonify({
            "reply": "The AI assistant isn't configured yet — set the GROQ_API_KEY environment variable and restart the app.",
            "history": [],
            "actions": [],
        }), 200

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()
    history = data.get("history") or []  # does NOT include the system message

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    system_prompt = f"""You are the AI assistant embedded in Budget Buddy, a personal expense tracker.
You help the user add, edit, delete, and understand their expenses using the tools provided.

Today's date is {date.today().isoformat()}.

Valid expense categories (use exactly one of these, never invent a new one):
{json.dumps(CATEGORIES, ensure_ascii=False)}

Guidelines:
- When the user describes a purchase in natural language (e.g. "spent 200 on lunch today"), extract the description, amount, category, and date, then call add_expense. Default the date to today if not mentioned.
- Pick the closest matching category from the list above based on the description.
- Use list_expenses or get_summary before answering questions about totals, trends, or specific expenses — never guess or make up numbers.
- If a delete/edit request is ambiguous (multiple expenses could match), call list_expenses first and ask the user which one they mean.
- After taking an action, confirm briefly and plainly what you did (one or two sentences).
- The app displays amounts with a $ sign; don't worry about currency conversion, just use the number given.
- Keep replies concise and friendly."""

    # Full message list sent to Groq: system prompt + prior turns + the new user message.
    # We keep the system message out of what we store/return so it can be regenerated
    # fresh each request (today's date, categories, etc. stay current).
    messages = [{"role": "system", "content": system_prompt}] + list(history) + [
        {"role": "user", "content": user_message}
    ]

    actions_taken = []

    try:
        for _ in range(5):  # cap the tool-use loop
            response = ai_client.chat.completions.create(
                model=AI_MODEL,
                max_tokens=1024,
                messages=messages,
                tools=AI_TOOLS,
                tool_choice="auto",
            )

            msg = response.choices[0].message

            assistant_entry = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                assistant_entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ]
            messages.append(assistant_entry)

            if msg.tool_calls:
                for tc in msg.tool_calls:
                    try:
                        tool_args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        tool_args = {}
                    result = run_ai_tool(tc.function.name, tool_args)
                    actions_taken.append(tc.function.name)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result),
                    })
                continue

            reply_text = (msg.content or "").strip()
            return jsonify({
                "reply": reply_text or "Done.",
                "history": messages[1:],  # drop the system message before returning
                "actions": actions_taken,
            })

        return jsonify({
            "reply": "That took more steps than expected — could you rephrase or simplify your request?",
            "history": messages[1:],
            "actions": actions_taken,
        })

    except Exception as ex:
        return jsonify({"reply": f"Sorry, I ran into an error talking to the AI service: {ex}", "history": history, "actions": []}), 200


if __name__ == "__main__":
    app.run(debug=True)