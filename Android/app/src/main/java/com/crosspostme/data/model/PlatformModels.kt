package com.crosspostme.data.model

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize
import java.util.*

/**
 * Platform Account Models - converted from Python Pydantic models
 * Following the backend API patterns from Copilot instructions
 */

@Parcelize
data class PlatformAccount(
    @SerializedName("id")
    val id: String = UUID.randomUUID().toString(),
    
    @SerializedName("user_id")
    val userId: String = "default",
    
    @SerializedName("platform")
    val platform: String, // facebook, craigslist, offerup, nextdoor
    
    @SerializedName("account_name")
    val accountName: String,
    
    @SerializedName("account_email")
    val accountEmail: String,
    
    @SerializedName("status")
    val status: String = "active", // active, suspended, flagged
    
    @SerializedName("created_at")
    val createdAt: String, // ISO string format
    
    @SerializedName("last_used")
    val lastUsed: String? = null
) : Parcelable

@Parcelize
data class PlatformAccountCreate(
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("account_name")
    val accountName: String,
    
    @SerializedName("account_email")
    val accountEmail: String
) : Parcelable