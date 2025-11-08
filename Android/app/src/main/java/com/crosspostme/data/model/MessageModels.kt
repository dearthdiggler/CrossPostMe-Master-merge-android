package com.crosspostme.data.model

import android.os.Parcelable
import com.google.gson.annotations.SerializedName
import kotlinx.parcelize.Parcelize
import java.util.*

/**
 * Message and Lead Models - converted from Python Pydantic models
 * Following the backend API patterns from Copilot instructions
 */

@Parcelize
data class IncomingMessage(
    @SerializedName("id")
    val id: String = UUID.randomUUID().toString(),
    
    @SerializedName("user_id")
    val userId: String = "default",
    
    @SerializedName("ad_id")
    val adId: String? = null,
    
    @SerializedName("platform")
    val platform: String, // facebook, craigslist, offerup, nextdoor
    
    @SerializedName("platform_message_id")
    val platformMessageId: String? = null,
    
    @SerializedName("sender_name")
    val senderName: String? = null,
    
    @SerializedName("sender_email")
    val senderEmail: String? = null,
    
    @SerializedName("sender_phone")
    val senderPhone: String? = null,
    
    @SerializedName("sender_profile_url")
    val senderProfileUrl: String? = null,
    
    @SerializedName("subject")
    val subject: String? = null,
    
    @SerializedName("message_text")
    val messageText: String,
    
    @SerializedName("message_type")
    val messageType: String = "inquiry", // inquiry, offer, question, complaint
    
    @SerializedName("source_type")
    val sourceType: String = "platform", // platform, email, parsed_notification
    
    @SerializedName("received_at")
    val receivedAt: String, // ISO string format
    
    @SerializedName("is_read")
    val isRead: Boolean = false,
    
    @SerializedName("is_responded")
    val isResponded: Boolean = false,
    
    @SerializedName("priority")
    val priority: String = "normal", // low, normal, high, urgent
    
    @SerializedName("raw_data")
    val rawData: Map<String, Any>? = null
) : Parcelable

@Parcelize
data class IncomingMessageCreate(
    @SerializedName("ad_id")
    val adId: String? = null,
    
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("platform_message_id")
    val platformMessageId: String? = null,
    
    @SerializedName("sender_name")
    val senderName: String? = null,
    
    @SerializedName("sender_email")
    val senderEmail: String? = null,
    
    @SerializedName("sender_phone")
    val senderPhone: String? = null,
    
    @SerializedName("sender_profile_url")
    val senderProfileUrl: String? = null,
    
    @SerializedName("subject")
    val subject: String? = null,
    
    @SerializedName("message_text")
    val messageText: String,
    
    @SerializedName("message_type")
    val messageType: String = "inquiry",
    
    @SerializedName("source_type")
    val sourceType: String = "platform",
    
    @SerializedName("priority")
    val priority: String = "normal",
    
    @SerializedName("raw_data")
    val rawData: Map<String, Any>? = null
) : Parcelable

@Parcelize
data class Lead(
    @SerializedName("id")
    val id: String = UUID.randomUUID().toString(),
    
    @SerializedName("user_id")
    val userId: String = "default",
    
    @SerializedName("ad_id")
    val adId: String? = null,
    
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("contact_name")
    val contactName: String? = null,
    
    @SerializedName("contact_email")
    val contactEmail: String? = null,
    
    @SerializedName("contact_phone")
    val contactPhone: String? = null,
    
    @SerializedName("interest_level")
    val interestLevel: String = "unknown", // unknown, low, medium, high, very_high
    
    @SerializedName("status")
    val status: String = "new", // new, contacted, qualified, negotiating, sold, lost
    
    @SerializedName("source_message_id")
    val sourceMessageId: String? = null,
    
    @SerializedName("last_contact_at")
    val lastContactAt: String? = null,
    
    @SerializedName("created_at")
    val createdAt: String, // ISO string format
    
    @SerializedName("notes")
    val notes: String? = null,
    
    @SerializedName("estimated_value")
    val estimatedValue: Double? = null,
    
    @SerializedName("tags")
    val tags: List<String> = emptyList()
) : Parcelable

@Parcelize
data class LeadCreate(
    @SerializedName("ad_id")
    val adId: String? = null,
    
    @SerializedName("platform")
    val platform: String,
    
    @SerializedName("contact_name")
    val contactName: String? = null,
    
    @SerializedName("contact_email")
    val contactEmail: String? = null,
    
    @SerializedName("contact_phone")
    val contactPhone: String? = null,
    
    @SerializedName("interest_level")
    val interestLevel: String = "unknown",
    
    @SerializedName("source_message_id")
    val sourceMessageId: String? = null,
    
    @SerializedName("notes")
    val notes: String? = null,
    
    @SerializedName("estimated_value")
    val estimatedValue: Double? = null,
    
    @SerializedName("tags")
    val tags: List<String> = emptyList()
) : Parcelable

@Parcelize
data class LeadUpdate(
    @SerializedName("contact_name")
    val contactName: String? = null,
    
    @SerializedName("contact_email")
    val contactEmail: String? = null,
    
    @SerializedName("contact_phone")
    val contactPhone: String? = null,
    
    @SerializedName("interest_level")
    val interestLevel: String? = null,
    
    @SerializedName("status")
    val status: String? = null,
    
    @SerializedName("last_contact_at")
    val lastContactAt: String? = null,
    
    @SerializedName("notes")
    val notes: String? = null,
    
    @SerializedName("estimated_value")
    val estimatedValue: Double? = null,
    
    @SerializedName("tags")
    val tags: List<String>? = null
) : Parcelable