import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import PredictFailureForm from "./PredictFailureForm";
import { mlApi } from "../api/client";

vi.mock("../api/client", () => ({
  mlApi: { predictFailure: vi.fn() },
}));

describe("PredictFailureForm", () => {
  it("affiche le formulaire avec les valeurs par defaut", () => {
    render(<PredictFailureForm />);
    expect(screen.getByLabelText("Température air (K)")).toHaveValue(300);
    expect(screen.getByRole("button", { name: /analyser le risque/i })).toBeInTheDocument();
  });

  it("appelle l'API et affiche le resultat apres une prediction reussie", async () => {
    mlApi.predictFailure.mockResolvedValueOnce({
      panne_predite: true,
      probabilite: 0.87,
      niveau_risque: "eleve",
      modele_version: "xgboost-v1",
    });

    render(<PredictFailureForm />);
    await userEvent.click(screen.getByRole("button", { name: /analyser le risque/i }));

    expect(mlApi.predictFailure).toHaveBeenCalledTimes(1);
    const statusRegion = await screen.findByRole("status");
    expect(statusRegion).toHaveTextContent("Panne probable");
    expect(statusRegion).toHaveTextContent("87.0 %");
  });

  it("affiche un message d'erreur si l'appel API echoue", async () => {
    mlApi.predictFailure.mockRejectedValueOnce(new Error("Erreur 503"));

    render(<PredictFailureForm />);
    await userEvent.click(screen.getByRole("button", { name: /analyser le risque/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Erreur 503");
  });
});
