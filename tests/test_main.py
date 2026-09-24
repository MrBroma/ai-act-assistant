from ai_act_assistant import main


def test_main_prints_greeting(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == "Hello from ai-act-assistant!\n"


def test_main_returns_none():
    result = main()
    assert result is None
