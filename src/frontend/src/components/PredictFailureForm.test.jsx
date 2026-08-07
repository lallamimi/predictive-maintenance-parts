import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PredictFailureForm from "./PredictFailureForm";
import { mlApi } from "../api/client";

vi.mock("../api/client", () => ({
  mlApi: { predictFailure: vi.fn() },
}));

describe("PredictFailureForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

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

  it("refuse une temperature hors plage physique avant tout appel API (C18 - couche Interface)", async () => {
    render(<PredictFailureForm />);
    const champTempAir = screen.getByLabelText("Température air (K)");

    // fireEvent.change plutot que userEvent.type : evite les etats
    // intermediaires invalides ("-" seul = NaN) d'un <input type="number">
    // controle par React lors d'une saisie caractere par caractere simulee.
    fireEvent.change(champTempAir, { target: { value: "-10" } });
    expect(champTempAir).toBeInvalid();

    await userEvent.click(screen.getByRole("button", { name: /analyser le risque/i }));

    expect(mlApi.predictFailure).not.toHaveBeenCalled();
  });
});
