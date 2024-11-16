from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

expenses = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        """👋 **Welcome to the Expense Splitter Bot!** 💸
Use /help to see a brief guide.
Use /add_expense <amount> <person> to log expenses.
Use /calculate to get each person's share.
Have fun😎"""
        )

def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
                """📚 **Expense Splitter Bot Help** 💸

Here are the available commands:
- /start - 🚀 Start the bot and see a welcome message.
- /help - ❓ Display this help message.
- /add_expense <amount> <person> - ➕ Add an expense for a person.  
Example: `/add_expense 100 John`
- /calculate - 🧮 Calculate and display how much each person owes or is owed.

Let’s make splitting expenses easy! 🎉"""
    )

def add_expense(update: Update, context: CallbackContext) -> None:
    try:
        amount = float(context.args[0])
        person = str(context.args[1])
        if person in expenses:
            expenses[person] += amount
        else:
            expenses[person] = amount
        update.message.reply_text(f"✅ Added expense of {amount} for {person}")
    except(IndexError, ValueError):
       update.message.reply_text("Usage: /add_expense <amount> <person>")

def calculate(update: Update, context: CallbackContext) -> None:
    global expenses
    if not expenses:
        update.message.reply_text("No expenses recorded.")
        return
    
    total = sum(expenses.values())
    people_count = len(expenses)
    share = total / people_count

    balances = {person: paid - share for person, paid in expenses.items()}

    creditors = {user: balance for user, balance in balances.items() if balance > 0}
    debtors = {user: balance for user, balance in balances.items() if balance < 0}

    payments = []
    for debtor, debt in debtors.items():
        debt = abs(debt)  # Convert negative debt to positive for calculations
        while debt > 0:
            creditor, credit = next(iter(creditors.items()))
            
            payment_amount = min(debt, credit)
            payments.append(f"💳 {debtor} should pay {creditor} {payment_amount:.3f}")

            debt -= payment_amount
            creditors[creditor] -= payment_amount

            if creditors[creditor] == 0:
                del creditors[creditor]


    update.message.reply_text(
        f"💰 Total expense: {total:.3f}\n"
        f"📊 Each person's share: {share:.3f}\n\n"
        f"⚖️ Balances:\n" + "\n".join(
            f"{user}: {'owes' if balance < 0 else 'is owed'} {abs(balance):.2f}"
            for user, balance in balances.items()
        ) + "\n\nPayment Instructions:\n" + "\n".join(payments)
    )

    expenses = {}

def main() -> None:
    updater = Updater("")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("add_expense", add_expense))
    dispatcher.add_handler(CommandHandler("calculate", calculate))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()