// Copyright 2018 Cameron Angus. All rights reserved.

#pragma once

#include "UObject/Object.h"
#include "UObject/ScriptMacros.h"
#include "AssetTypeActions_Base.h"
#include "KCKantanInfoAsset.generated.h"


UCLASS(Abstract, HideDropdown)
class UKCKantanInfoAssetBase : public UObject
{
	GENERATED_BODY()

public:
	UKCKantanInfoAssetBase() {}

public:
	FSimpleDelegate DefaultAction;

public:
	virtual void PerformAssetAction() const
	{
		DefaultAction.ExecuteIfBound();
	}
};

UCLASS(HideDropdown)
class UKCKantanInfoAsset : public UKCKantanInfoAssetBase
{
	GENERATED_BODY()
};

UCLASS(HideDropdown)
class UKCKantanDocsAsset : public UKCKantanInfoAssetBase
{
	GENERATED_BODY()
};


namespace KCKantanInstallation
{
	class FAssetTypeActions_KantanInfo : public FAssetTypeActions_Base
	{
	public:
		// IAssetTypeActions Implementation
		virtual UClass* GetSupportedClass() const override;
		virtual bool CanFilter() override { return false; }
		virtual bool CanLocalize() const override { return false; }
		virtual bool CanMerge() const override { return false; }
		virtual FText GetName() const override { return NSLOCTEXT("AssetTypeActions", "AssetTypeActions_KantanInfo", "Kantan Info Asset"); }
		virtual FColor GetTypeColor() const override { return FColor(0, 255, 255); }
		virtual uint32 GetCategories() override;
		virtual bool HasActions(const TArray<UObject*>& InObjects) const override { return true; }
		virtual void GetActions(const TArray<UObject*>& InObjects, FMenuBuilder& MenuBuilder) override;
		virtual void OpenAssetEditor(const TArray<UObject*>& InObjects, TSharedPtr<class IToolkitHost> EditWithinLevelEditor = TSharedPtr<IToolkitHost>()) override;
		virtual bool IsImportedAsset() const override { return false; }
		// End IAssetTypeActions
	};
}

