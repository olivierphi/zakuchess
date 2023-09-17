from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import DailyChallenge


class DailyChallengeAdminForm(forms.ModelForm):
    class Meta:
        model = DailyChallenge
        fields = ("id", "fen", "bot_first_move", "intro_turn_speech_square")

    def clean_bot_first_move(self) -> str:
        return self.cleaned_data["bot_first_move"].lower()


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    form = DailyChallengeAdminForm

    list_display = ("id", "fen", "bot_first_move", "fen_before_bot_first_move", "teams")
    readonly_fields = ("game_preview",)

    @admin.display(description="Game preview")
    def game_preview(self, instance: DailyChallenge) -> str:
        # Quick and (very) dirty management of the game preview
        return mark_safe(
            """
            <iframe
                id="preview-iframe"
                style="width: 400px; aspect-ratio: 1 / 1.3; border: solid navy 1px;">
            </iframe>
            
            <script>
            (function() {
                const adminPreviewUrl = "${ADMIN_PREVIEW_URL}";
                
                const previewIFrame = document.getElementById("preview-iframe");
                
                const fenInput = document.getElementById("id_fen");
                const botFirstMoveInput = document.getElementById("id_bot_first_move");
                const introTurnSpeechSquareInput = document.getElementById("id_intro_turn_speech_square");
                
                function updatePreview() {
                    previewIFrame.src = adminPreviewUrl + "?" + (new URLSearchParams({
                        fen: fenInput.value,
                        bot_first_move: botFirstMoveInput.value,
                        intro_turn_speech_square: introTurnSpeechSquareInput.value,
                    })).toString();
                }
                
                fenInput.addEventListener("keyup", updatePreview);
                botFirstMoveInput.addEventListener("keyup", updatePreview);
                introTurnSpeechSquareInput.addEventListener("keyup", updatePreview);
                
                setTimeout(updatePreview, 1000);
            })();
            </script>
            """.replace(
                "${ADMIN_PREVIEW_URL}", reverse("daily_challenge:admin_game_preview")
            )
        )
