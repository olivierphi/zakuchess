from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import DailyChallenge


class DailyChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = DailyChallenge
        fields = ("id", "fen", "bot_first_move", "intro_turn_speech_square")

    class Media:
        js = ("daily_challenge/admin_game_preview.js",)

    def clean_bot_first_move(self) -> str:
        return self.cleaned_data["bot_first_move"].lower()


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    form = DailyChallengeAdminForm

    list_display = ("id", "fen", "bot_first_move", "fen_before_bot_first_move", "teams")
    readonly_fields = (
        "game_update",
        "game_preview",
    )

    @admin.display(description="Game update")
    def game_update(self, instance: DailyChallenge) -> str:
        return mark_safe(
            """
            <input type="text" class="vTextField" maxlength="5" id="id_update_game">
            <div class="help" id="id_update_game_helptext" style="margin-left: 0;">
                <ul>
                    <li><code>[square]:x!</code>: removes the piece from a square</li>
                    <li><code>[square]:R!</code>: adds a piece to a square (here, a white rook)</li>
                </ul>
            </div>
            """
        )

    @admin.display(description="Game preview")
    def game_preview(self, instance: DailyChallenge) -> str:
        # Quick and (very) dirty management of the game preview
        return mark_safe(
            """
            <div id="admin-preview-url-holder" style="display: none;">${ADMIN_PREVIEW_URL}</div>
            
            <iframe
                id="preview-iframe"
                style="width: 400px; aspect-ratio: 1 / 1.3; border: solid navy 1px;">
            </iframe>
            
            <div style="margin: 1rem 0;">
                Can always help: <a href="https://www.dailychess.com/chess/chess-fen-viewer.php" 
                    rel="noreferrer noopener" >www.dailychess.com/chess/chess-fen-viewer.php</a>
            </div>
            
            """.replace(
                "${ADMIN_PREVIEW_URL}", reverse("daily_challenge:admin_game_preview")
            )
        )
