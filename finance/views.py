
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Transaction


@login_required
def add_transaction(request):

    if request.method == 'POST':

        transaction = Transaction(
            farmer=request.user,
            transaction_type=request.POST['transaction_type'],
            title=request.POST['title'],
            amount=request.POST['amount'],
            date=request.POST['date'],
            description=request.POST['description']
        )

        transaction.save()

        return redirect('finance_dashboard')

    return render(request, 'finance/add_transaction.html')


@login_required
def finance_dashboard(request):

    transactions = Transaction.objects.filter(
        farmer=request.user
    ).order_by('-date')

    total_income = sum(
        t.amount for t in transactions
        if t.transaction_type == 'Income'
    )

    total_expense = sum(
        t.amount for t in transactions
        if t.transaction_type == 'Expense'
    )

    profit = total_income - total_expense

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'profit': profit
    }

    return render(request, 'finance/dashboard.html', context)


@login_required
def edit_transaction(request, id):

    transaction = get_object_or_404(
        Transaction,
        id=id,
        farmer=request.user
    )

    if request.method == 'POST':

        transaction.transaction_type = request.POST['transaction_type']
        transaction.title = request.POST['title']
        transaction.amount = request.POST['amount']
        transaction.date = request.POST['date']
        transaction.description = request.POST['description']

        transaction.save()

        return redirect('finance_dashboard')

    return render(
        request,
        'finance/edit_transaction.html',
        {'transaction': transaction}
    )


@login_required
def delete_transaction(request, id):

    transaction = get_object_or_404(
        Transaction,
        id=id,
        farmer=request.user
    )

    if request.method == 'POST':
        transaction.delete()
        return redirect('finance_dashboard')

    return render(
        request,
        'finance/delete_transaction.html',
        {'transaction': transaction}
    )
