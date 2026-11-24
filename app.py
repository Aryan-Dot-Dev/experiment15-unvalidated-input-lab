from flask import Flask, request


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username', '')
        quantity = request.form.get('quantity', '1')

        # Intentionally vulnerable for Experiment 15:
        # no input validation and no output escaping.
        quantity_value = int(quantity)
        total = quantity_value * 100

        return f'''
            <h2>Registration Result</h2>
            <p>Welcome, {username}</p>
            <p>Quantity: {quantity_value}</p>
            <p>Total: Rs. {total}</p>
            <a href="/">Back</a>
        '''

    return '''
        <h2>Unvalidated Input Demonstration</h2>
        <form method="POST">
            <label>Username:</label>
            <input name="username">
            <br><br>
            <label>Quantity:</label>
            <input name="quantity" value="1">
            <br><br>
            <button type="submit">Submit</button>
        </form>
    '''


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
