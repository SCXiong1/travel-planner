"""结算业务逻辑"""


def get_settlement(db, trip_id: int) -> dict:
    acts = db.execute(
        """SELECT expense_amount, expense_payer, expense_split
           FROM activities a
           JOIN days d ON a.day_id = d.id
           WHERE d.trip_id = ? AND a.deleted_at IS NULL AND d.deleted_at IS NULL
             AND a.expense_amount IS NOT NULL AND a.expense_amount > 0""",
        (trip_id,),
    ).fetchall()

    sd_paid = 0
    sg_paid = 0
    sd_owes = 0
    sg_owes = 0

    for act in acts:
        amount = act["expense_amount"]
        payer = act["expense_payer"]
        split = act["expense_split"]

        if payer == "sd":
            sd_paid += amount
        else:
            sg_paid += amount

        if split == "equal":
            sd_owes += amount / 2
            sg_owes += amount / 2
        else:  # assign
            if payer == "sd":
                sd_owes += amount
            else:
                sg_owes += amount

    total = sd_paid + sg_paid
    sd_balance = sd_paid - sd_owes
    sg_balance = sg_paid - sg_owes

    return {
        "sd_paid": sd_paid,
        "sg_paid": sg_paid,
        "total": total,
        "sd_owes": round(sd_owes, 2),
        "sg_owes": round(sg_owes, 2),
        "sd_balance": round(sd_balance, 2),
        "sg_balance": round(sg_balance, 2),
        "balance": round(abs(sd_balance), 2),
    }
