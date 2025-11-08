package com.crosspostme.data.model

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize
import java.util.*

/**
 * Ad Models - converted from Python Pydantic models
 * Following the backend API patterns from Copilot instructions
 */

@Parcelize
data class Ad(
    @SerializedName("id")
    val id: String = UUID.randomUUID().toString(),
    
    @SerializedName("user_id")
    val userId: String = "default",
    
    @SerializedName("title")
    val title: String,
    
    @SerializedName("description")
    val description: String,
    
    @SerializedName("price")
    val price: Double,
    
    @SerializedName("category")
    val category: String,
    
    @SerializedName("location")
    val location: String,
    
    @SerializedName("images")
    val images: List<String> = emptyList(),
    
    @SerializedName("platforms")
    val platforms: List<String> = emptyList(), // Which platforms to post to
    
    @SerializedName("status")
    val status: String = "draft", // draft, scheduled, posted, paused
    
    @SerializedName("created_at")
    val createdAt: String, // ISO string format
    
    @SerializedName("scheduled_time")
    val scheduledTime: String? = null,
    
    @SerializedName("auto_renew")
    val autoRenew: Boolean = false
) : Parcelable

@Parcelize
data class AdCreate(
    @SerializedName("user_id")
    val userId: String = "default",
    
    @SerializedName("title")
    val title: String,
    
    @SerializedName("description")
    val description: String,
    
    @SerializedName("price")
    val price: Double,
    
    @SerializedName("category")
    val category: String,
    
    @SerializedName("location")
    val location: String,
    
    @SerializedName("images")
    val images: List<String> = emptyList(),
    
    @SerializedName("platforms")
    val platforms: List<String> = emptyList(),
    
    @SerializedName("scheduled_time")
    val scheduledTime: String? = null,
    
    @SerializedName("auto_renew")
    val autoRenew: Boolean = false
) : Parcelable

@Parcelize
data class AdUpdate(
    @SerializedName("title")
    val title: String? = null,
    
    @SerializedName("description")
    val description: String? = null,
    
    @SerializedName("price")
    val price: Double? = null,
    
    @SerializedName("category")
    val category: String? = null,
    
    @SerializedName("location")
    val location: String? = null,
    
    @SerializedName("images")
    val images: List<String>? = null,
    
    @SerializedName("platforms")
    val platforms: List<String>? = null,
    
    @SerializedName("status")
    val status: String? = null,
    
    @SerializedName("scheduled_time")
    val scheduledTime: String? = null,
    
    @SerializedName("auto_renew")
    val autoRenew: Boolean? = null
) : Parcelable

@Parcelize
data class PostedAd(
    @SerializedName("id")
    val id: String = UUID.randomUUID().toString(),
    
    @SerializedName("ad_id")
    val adId: String,
    
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("platform_ad_id")
    val platformAdId: String? = null,
    
    @SerializedName("post_url")
    val postUrl: String? = null,
    
    @SerializedName("posted_at")
    val postedAt: String, // ISO string format
    
    @SerializedName("status")
    val status: String = "active", // active, expired, removed, flagged
    
    @SerializedName("views")
    val views: Int = 0,
    
    @SerializedName("clicks")
    val clicks: Int = 0,
    
    @SerializedName("leads")
    val leads: Int = 0
) : Parcelable

@Parcelize
data class PostedAdCreate(
    @SerializedName("ad_id")
    val adId: String,
    
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("platform_ad_id")
    val platformAdId: String? = null,
    
    @SerializedName("post_url")
    val postUrl: String? = null
) : Parcelable