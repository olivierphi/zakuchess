import { Controller } from "@hotwired/stimulus"

import type { PieceSymbol, PlayerSide, TeamMember, TeamMembersRole } from "../chess-domain"
import type { TeamMembersByRoleBySide } from "../chess-domain"
import type { ActionEvent } from "@hotwired/stimulus/dist/types/core/action_event"
import { getChessPieceName, getChessPieceSymbol } from "../chess-helpers"

type TeamMembersControllerMetadata = {
    teamMembersByRoleBySide: TeamMembersByRoleBySide | null
}

export default class extends Controller {
    static targets = [
        "selectedTeamMemberContainer",
        "selectedTeamMemberFirstName",
        "selectedTeamMemberLastName",
        "selectedTeamMemberChessEquivalent",
        "teamMemberUnitDisplay",
    ]

    declare selectedTeamMemberContainerTarget: HTMLElement
    declare selectedTeamMemberFirstNameTargets: HTMLElement[]
    declare selectedTeamMemberLastNameTargets: HTMLElement[]
    declare selectedTeamMemberChessEquivalentTarget: HTMLElement
    declare teamMemberUnitDisplayTargets: HTMLElement[]

    metadata: TeamMembersControllerMetadata | null = null

    connect() {
        super.connect()
        if (this.metadata === null) {
            this.setMetadataFromDOM()
        }
    }

    private displayTeamMemberForPiece(event: ActionEvent): void {
        const piece = event.currentTarget as HTMLElement
        const playerSide = piece.dataset.playerSide as PlayerSide
        const role = piece.dataset.teamMemberRole as TeamMembersRole
        const pieceSymbol = role.charAt(0) as PieceSymbol
        const teamMember = this.metadata!.teamMembersByRoleBySide![playerSide][role]
        this.selectedTeamMemberContainerTarget.classList.remove("hidden")
        this.displayTeamMemberInfo(teamMember, pieceSymbol)
        this.displayTeamMemberUnitDisplay(playerSide, pieceSymbol)
    }

    private displayTeamMemberInfo(teamMember: TeamMember, pieceSymbol: PieceSymbol): void {
        // Slight appearance effect:
        const toggleTextAppearance = (operation: "add" | "remove") => {
            this.element.querySelectorAll("p").forEach((p) => p.classList[operation]("appearance"))
        }
        toggleTextAppearance("remove")
        setTimeout(toggleTextAppearance.bind(null, "add"), 100)

        this.selectedTeamMemberFirstNameTargets.forEach((el) => (el.innerText = teamMember.first_name))
        this.selectedTeamMemberLastNameTargets.forEach((el) => (el.innerText = teamMember.last_name))
        this.selectedTeamMemberChessEquivalentTarget.innerHTML = [
            getChessPieceName(pieceSymbol),
            `<span class="chess-symbol">${getChessPieceSymbol(pieceSymbol)}</span>`,
        ].join(" ")
    }

    private displayTeamMemberUnitDisplay(playerSide: PlayerSide, pieceSymbol: PieceSymbol): void {
        this.teamMemberUnitDisplayTargets.forEach((teamMemberUnitDisplay) => {
            teamMemberUnitDisplay.classList.value = `piece side-${playerSide} piece-${pieceSymbol}`
        })
    }

    private setMetadataFromDOM(): void {
        const teamMembersByRoleBySideDataHolder = this.element.querySelector<HTMLElement>(
            "[data-team-members-by-role-by-side]",
        )!
        this.metadata = {
            teamMembersByRoleBySide: JSON.parse(
                teamMembersByRoleBySideDataHolder.dataset.teamMembersByRoleBySide!,
            ) as TeamMembersByRoleBySide,
        }
    }
}
