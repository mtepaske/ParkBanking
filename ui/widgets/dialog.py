from copy import deepcopy
from pathlib import Path
from typing import Any, Literal, TypedDict

from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, HorizontalGroup, VerticalGroup
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    DirectoryTree,
    Input,
    Label,
    MaskedInput,
    Select,
    Static,
)
from textual.widgets.button import ButtonVariant

from models.account import Account
from models.transactions import Transaction
from services.date import end_of_fy, get_str_from_date, start_of_fy


class ButtonConfig(TypedDict):
    variant: ButtonVariant
    returns: Any
    disabled: bool


DEFAULT_BUTTONS = {
    "Confirm": ButtonConfig(variant="success", returns=True, disabled=False)
}


class Dialog(ModalScreen):

    def __init__(
        self,
        message: str,
        context: str | None = None,
        cancel_button: str = "Cancel",
    ):
        super().__init__()
        self.message = message
        self.context = context
        self.cancel_button = cancel_button
        self.buttons = DEFAULT_BUTTONS

    def compose(self) -> ComposeResult:

        with VerticalGroup():

            yield from self.compose_title()
            yield from self.compose_content()
            yield from self.compose_buttons()

    def compose_title(self) -> ComposeResult:

        with VerticalGroup(classes="dialog-title"):

            if self.context is not None:

                if len(self.message) >= len(self.context):
                    with HorizontalGroup():
                        yield Static(self.message, classes="message")

                    with Horizontal():
                        yield Static(self.context, classes="context")

                else:
                    with Horizontal():
                        yield Static(self.message, classes="message")

                    with HorizontalGroup():
                        yield Static(self.context, classes="context")

            else:
                with HorizontalGroup():
                    yield Static(self.message, classes="message")

    def compose_content(self) -> ComposeResult:

        yield from ()

    def compose_buttons(self) -> ComposeResult:

        for name, value in self.buttons.items():

            with Horizontal(classes="row"):
                yield Button(
                    name,
                    variant=value["variant"],
                    disabled=value["disabled"],
                    id=name,
                )

        with Horizontal(classes="row"):
            yield Button(
                self.cancel_button,
                variant="error",
                id=self.cancel_button,
            )

    @on(Button.Pressed)
    def press(self, event: Button.Pressed):

        id = event.button.id

        if id == self.cancel_button:
            self.dismiss(False)

        elif id in self.buttons:
            self.dismiss(self.buttons[id]["returns"])

    def switch_diabled(self, button_id: str, disabled: bool) -> None:

        button = self.query_one(f"#{button_id}", Button)
        button.disabled = disabled


class AppendReplace(Dialog):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttons = {
            "Add To": ButtonConfig(variant="success", returns="append", disabled=False),
            "Replace": ButtonConfig(
                variant="warning", returns="replace", disabled=False
            ),
        }


class ImportFile(Dialog):

    def __init__(self, import_folder: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self.import_folder = import_folder
        self.buttons["Confirm"]["disabled"] = True

    def compose_content(self) -> ComposeResult:

        with HorizontalGroup(classes="tree-row"):
            yield DirectoryTree(
                str(self.import_folder), classes="tree", id="balance-tree"
            )

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:

        for button in self.buttons:
            self.buttons[button]["returns"] = event.path
            self.switch_diabled(button, False)
            break


class SelectDateRange(Dialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_date = get_str_from_date(start_of_fy())
        self.end_date = get_str_from_date(end_of_fy())
        self.buttons["Confirm"]["returns"] = (self.start_date, self.end_date)

    def compose_content(self) -> ComposeResult:

        with Horizontal(classes="row"):
            yield Label("Start Date")
            yield Label("End Date")

        with Horizontal(classes="row"):
            yield MaskedInput("9999-99-99", value=str(self.start_date), id="start-date")
            yield MaskedInput("9999-99-99", value=str(self.end_date), id="end-date")

    @on(MaskedInput.Changed)
    def change_date(self, event: MaskedInput.Changed):

        match event.control.id:

            case "start-date":
                self.start_date = self.query_one("#start-date", MaskedInput).value

            case "end-date":
                self.end_date = self.query_one("#end-date", MaskedInput).value

        self.buttons["Confirm"]["returns"] = (self.start_date, self.end_date)


class AccountPicker(Dialog):

    def __init__(self, accounts: list[Account], **kwargs) -> None:

        super().__init__(**kwargs)
        self.switch_diabled("Confirm", True)
        # self.buttons["Confirm"]["disabled"] = True

        self.accounts = accounts
        self.keys = {}
        self.buttons["Comfirm"]["returns"] = None
        self.buttons["No Account"] = ButtonConfig(
            variant="warning", returns=None, disabled=False
        )

    def compose(self) -> ComposeResult:

        yield from self.compose_title()
        yield from self.compose_buttons()
        yield from self.compose_content()

    def compose_content(self) -> ComposeResult:

        with Horizontal(classes="row"):
            yield Static(
                f"Account Selected: {self.buttons['Confirm']['returns']}", id="selected"
            )
        with Horizontal(classes="row"):
            yield DataTable(zebra_stripes=True, cursor_type="row", id="accounts_1")
            yield DataTable(zebra_stripes=True, cursor_type="row", id="accounts_2")

    def on_mount(self) -> None:

        account_1 = self.query_one("#accounts-1", DataTable)
        account_1.add_columns("Account ID", "Name", "Site Number", "Active")

        account_2 = self.query_one("#accounts-2", DataTable)
        account_2.add_columns("Account ID", "Name", "Site Number", "Active")

        midpoint = len(self.accounts) // 2

        for index in range(midpoint):
            key = account = self.accounts[index]
            account_1.add_row(
                Text(f"{account.account_id}", style="cyan"),
                account.name,
                account.site_number,
                account.active,
            )
            self.keys[key] = Account

        for index in range(midpoint, len(self.accounts)):
            account = self.accounts[index]
            key = account_2.add_row(
                Text(f"{account.account_id}", style="cyan"),
                account.name,
                account.site_number,
                account.active,
            )
            self.keys[key] = Account

    @on(DataTable.RowSelected)
    def account_selected(self, event: DataTable.RowSelected):

        self.buttons["Confirm"]["returns"] = self.keys[event.row_key]
        self.switch_diabled("Confirm", False)
        self.query_one("#selected", Static).update(
            f"Account Selected: {self.buttons['Confirm']['returns']}"
        )


class EnterInput(Dialog):

    def __init__(self, input_type: Literal["money", "str", "date"], **kwargs):
        super().__init__(**kwargs)
        self.switch_diabled("#Confirm", True)

        match input_type:

            case "money":
                self.placeholder = "0"
                self.prefix = "$"

    def compose_content(self) -> ComposeResult:

        with Horizontal(classes="row"):
            yield Static(self.prefix, classes="prefix")
            yield Input(value=self.placeholder)

    @on(Input.Changed)
    def change_value(self, event: Input.Changed):

        self.buttons["Confirm"]["returns"] = event.control.value
        self.switch_diabled("#Confirm", False)


class ReviewBalance(Dialog):

    def __init__(self, accounts: list[Account], payments: list[Transaction], **kwargs):
        super().__init__(**kwargs)
        self.accounts = deepcopy(accounts)
        self.payments = payments

        self.buttons["Confirm"]["returns"] = self.accounts

    def compose_content(self) -> ComposeResult:

        yield DataTable(zebra_stripes=True, cursor_type="row", id="history")

    def on_mount(self) -> None:

        review_table = self.query_one("#history", DataTable)
        review_table.add_columns(
            "Account",
            "Old Remaining",
            "Old Outstanding",
            "Old Credit",
            " -> ",
            "Amount",
            " -> ",
            "New Remaining",
            "New Outstanding",
            "New Credit",
            "New Total Balance",
        )

        for payment in self.payments:
            account = payment.account
            assert account is not None
            balance = account.balance
            assert balance is not None

            old_balance = (balance.remaining, balance.outstanding, balance.credit)

            if payment.amount > 0:
                new_balance = balance.add_payment(payment.amount)
                sign = "-"
            else:
                new_balance = balance.add_charge(payment.amount)
                sign = "+"

            review_table.add_row(
                Text(f"{account.site_number}: {account.name}", style="cyan"),
                Text(f"${old_balance[0]:,.2f}", style="red"),
                (
                    Text(f"${old_balance[1]:,.2f}", style="red")
                    if old_balance[1] != 0
                    else ""
                ),
                (
                    Text(f"${old_balance[2]:,.2f}", style="red")
                    if old_balance[2] != 0
                    else ""
                ),
                Text(" -> ", style="cyan"),
                Text(f"{sign}${abs(payment.amount):,.2f}", style="cyan"),
                Text(" -> ", style="cyan"),
                Text(f"${new_balance[0]:,.2f}", style="green"),
                (
                    Text(f"${new_balance[1]:,.2f}", style="green")
                    if new_balance[1] != 0
                    else ""
                ),
                (
                    Text(f"${new_balance[2]:,.2f}", style="green")
                    if new_balance[2] != 0
                    else ""
                ),
                Text(
                    f"${new_balance[0] + new_balance[1] - new_balance[2]:,.2f}",
                    style="cyan",
                ),
            )

            balance.apply_new_amounts(new_balance)


class ProccessUnknown(Dialog):

    def __init__(self, accounts: list[Account], **kwargs):

        super().__init__(**kwargs)
        self.cancel_button = "Skip Rest"
        self.buttons = {
            "Alias": ButtonConfig(variant="success", returns=None, disabled=True),
            "Word": ButtonConfig(variant="success", returns="ignore", disabled=False),
            "Skip": ButtonConfig(variant="error", returns="skip", disabled=False),
        }
        self.accounts = (
            (f"{account.site_number}: {account.name}", account) for account in accounts
        )

    def compose_content(self) -> ComposeResult:

        with Horizontal(classes="row"):
            yield Select(
                self.accounts,
                prompt="Select Account",
                type_to_search=True,
                id="account",
            )

    @on(Select.Changed)
    def account_selected(self):

        value = self.query_one("#account", Select).value

        if isinstance(value, tuple):
            self.switch_diabled("Alias", False)
            self.buttons["Alias"]["returns"] = value[1]


class EditHistory(Dialog):

    def __init__(self, history_item: Transaction, **kwargs) -> None:
        super().__init__(**kwargs)
        self.history_item = history_item
        self.buttons["Confirm"]["returns"] = self.history_item

    def compose_content(self) -> ComposeResult:

        with Horizontal(classes="row"):
            yield Label("Date:")
            yield MaskedInput("9999-99-99", value=self.history_item.date)

        with Horizontal(classes="row"):
            yield Label("Amount:")
            yield Input(value=str(self.history_item.amount))

        with Horizontal(classes="row"):
            yield Label("Description:")
            yield Input(value=self.history_item.type)
