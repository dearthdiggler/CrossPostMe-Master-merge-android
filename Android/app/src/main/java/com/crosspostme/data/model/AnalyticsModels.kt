package com.crosspostme.data.model

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize
import java.util.*

/**
 * Analytics and AI Models - converted from Python Pydantic models
 * Following the backend API patterns from Copilot instructions
 */

@Parcelize
data class AdAnalytics(
    @SerializedName("ad_id")
    val adId: String,
    
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("views")
    val views: Int = 0,
    
    @SerializedName("clicks")
    val clicks: Int = 0,
    
    @SerializedName("leads")
    val leads: Int = 0,
    
    @SerializedName("messages")
    val messages: Int = 0,
    
    @SerializedName("conversion_rate")
    val conversionRate: Double = 0.0,
    
    @SerializedName("date")
    val date: String // ISO string format
) : Parcelable

@Parcelize
data class DashboardStats(
    @SerializedName("total_ads")
    val totalAds: Int,
    
    @SerializedName("active_ads")
    val activeAds: Int,
    
    @SerializedName("total_posts")
    val totalPosts: Int,
    
    @SerializedName("total_views")
    val totalViews: Int,
    
    @SerializedName("total_leads")
    val totalLeads: Int,
    
    @SerializedName("platforms_connected")
    val platformsConnected: Int
) : Parcelable

// AI Generation Models
@Parcelize
data class AIAdRequest(
    @SerializedName("product_name")
    val productName: String,
    
    @SerializedName("product_details")
    val productDetails: String,
    
    @SerializedName("price")
    val price: Double,
    
    @SerializedName("category")
    val category: String,
    
    @SerializedName("tone")
    val tone: String = "professional" // professional, casual, urgent
) : Parcelable

@Parcelize
data class AIAdResponse(
    @SerializedName("title")
    val title: String,
    
    @SerializedName("description")
    val description: String,
    
    @SerializedName("suggested_categories")
    val suggestedCategories: List<String>,
    
    @SerializedName("keywords")
    val keywords: List<String>
) : Parcelable