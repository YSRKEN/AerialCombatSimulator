package jp.ysrken.kacs.model;

import java.util.Arrays;

public enum WeaponType {
    None,
    SmallGun,
    MediumGun,
    LargeGun,
    Secondary,
    Torpedo,
    LandingCraft,
    CarrierFighter,
    CarrierBomber,
    FighterBomber,
    Jet,
    CarrierAttacker,
    CarrierReconn,
    Saiun,
    SeaFighter,
    SeaBomber,
    SeaReconn,
    AntiSubPlane,
    FlyingBoat,
    SurfaceRadar,
    AirRadar,
    Engine,
    AntiAirShell,
    ArmorShell,
    AntiAirGun,
    AntiAirFireDirector,
    DepthChargeLauncher,
    DepthCharge,
    Sonar,
    DamageController,
    ExtraArmor,
    LandAttacker,
    LandFighter1,
    LandFighter2,
    AviationPersonnel,
    Other,
    LandReconn;

    private final int value;

    private WeaponType() {
        this.value = 0;
    }

    private WeaponType(final int value) {
        this.value = value;
    }

    public static WeaponType of(int value) {
        if (value < 0)
            return WeaponType.None;
        if (value > WeaponType.LandReconn.ordinal())
            return WeaponType.None;
        return WeaponType.values()[value];
    }
}