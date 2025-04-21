from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///performance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class PerformanceEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    metric = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PerformanceEntry {self.metric}: {self.value} ({self.date.strftime("%Y-%m-%d")})>'

@app.route('/')
def index():
    entries = PerformanceEntry.query.order_by(PerformanceEntry.date.desc()).all()
    return render_template('index.html', entries=entries)

@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        category = request.form.get('category')
        metric = request.form.get('metric')
        value = request.form.get('value')
        note = request.form.get('note')

        try:
            value = float(value)
        except ValueError:
            flash("Please enter a valid number for the metric value.", "error")
            return redirect(url_for('add_entry'))

        entry = PerformanceEntry(category=category, metric=metric, value=value, note=note)
        db.session.add(entry)
        db.session.commit()
        flash("Performance entry added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_entry.html')

@app.route('/analytics')
def analytics():
    from sqlalchemy import func
    analytics_data = (
        db.session.query(
            PerformanceEntry.category,
            func.count(PerformanceEntry.id).label('entry_count'),
            func.avg(PerformanceEntry.value).label('average_value')
        )
        .group_by(PerformanceEntry.category)
        .all()
    )
    return render_template('analytics.html', analytics_data=analytics_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
